import time
from urllib.parse import urlencode

import pytest
import sentry_sdk
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import scale_batch_size_phase

# Drives the agent's context snowball: ask for the return policy. The
# search_policies tool hands the whole help-centre export to the model as raw
# HTML, so this one turn costs tens of thousands of input tokens on the
# orchestrator's gen_ai.chat span. The answer is right and nothing errors.
#
# One question per run at most, to bound OpenRouter spend: each run is roughly
# 20x the input tokens of an ordinary turn.

# test_basic_checkout.py is on +12, test_agent_cexp.py on +6 and
# test_agent_orders.py on +18.
PHASE_OFFSET_HOURS = 0

TURN_TIMEOUT = 90

# Seconds to leave the trace open before navigating away, so Sentry's browser
# SDK flushes the session span.
TRACE_FLUSH_SECONDS = 12


def _click(driver, element_id, timeout=TURN_TIMEOUT):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, element_id))
    )
    element.click()
    return element


def _wait_for_card(driver, css_selector, timeout=TURN_TIMEOUT):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


# Skip before the Sauce session is created.
@pytest.fixture(autouse=True)
def _skip_when_off_phase(random):
    if scale_batch_size_phase(1, random, PHASE_OFFSET_HOURS) == 0:
        pytest.skip("not running this round — off-phase for this test")


def test_agent_policy(desktop_web_1browser_driver, endpoints, sleep_length):
    driver = desktop_web_1browser_driver

    # flask is the backend the agent's other tools talk to; kept for parity.
    query_string = {"backend": "flask"}
    # The widget only mounts on Home, so this is the site root.
    url = endpoints.react_endpoint + "?" + urlencode(query_string)

    sentry_sdk.metrics.incr(
        key="test_agent_policy.iteration.started", value=1, tags=query_string
    )

    try:
        driver.get(url)

        _click(driver, "home-ask-agent")
        time.sleep(sleep_length())

        # The one turn — the oversized policy lookup.
        _click(driver, "chat-starter-returns")
        _wait_for_card(driver, "#chat-policy")

        sentry_sdk.metrics.incr(
            key="test_agent_policy.iteration.completed", value=1, tags=query_string
        )

        time.sleep(TRACE_FLUSH_SECONDS)

    except (NoSuchElementException, TimeoutException) as err:
        sentry_sdk.metrics.incr(
            key="test_agent_policy.iteration.abandoned",
            value=1,
            tags=dict(query_string, reason=err.__class__.__name__),
        )
    except Exception as err:
        sentry_sdk.capture_exception(err)
        print(err)
