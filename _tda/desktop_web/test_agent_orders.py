import time
from urllib.parse import urlencode

import pytest
import sentry_sdk
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import scale_batch_size_phase

# Drives the agent's ghost cancellation: list the customer's orders, then
# cancel order #445. Flask's refund call times out and the endpoint answers
# 500, but the cancel_order tool treats that as success and the agent tells the
# customer the order is cancelled. The failure only shows in the trace.
#
# Order #445 is left in cancel_requested, which is still cancellable, so runs
# need no reset between them.
#
# One conversation per run at most. Each cancel holds a flask worker for the
# full mock payment provider delay, and each turn is several LLM calls.

# test_basic_checkout.py is on +12 and test_agent_cexp.py on +6.
PHASE_OFFSET_HOURS = 18

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


def test_agent_orders(desktop_web_1browser_driver, endpoints, sleep_length):
    driver = desktop_web_1browser_driver

    # flask is the only backend the agent's tools talk to.
    query_string = {"backend": "flask"}
    # The widget only mounts on Home, so this is the site root.
    url = endpoints.react_endpoint + "?" + urlencode(query_string)

    sentry_sdk.metrics.incr(
        key="test_agent_orders.iteration.started", value=1, tags=query_string
    )

    try:
        driver.get(url)

        _click(driver, "home-ask-agent")
        time.sleep(sleep_length())

        # Turn 1 — list orders. The cancel pill only appears after this.
        _click(driver, "chat-starter-orders")
        _wait_for_card(driver, "#chat-orders")

        # Turn 2 — cancel #445, the ghost failure.
        time.sleep(sleep_length())
        _click(driver, "chat-pill-cancel-order")
        _wait_for_card(driver, "#chat-order")

        sentry_sdk.metrics.incr(
            key="test_agent_orders.iteration.completed", value=1, tags=query_string
        )

        time.sleep(TRACE_FLUSH_SECONDS)

    except (NoSuchElementException, TimeoutException) as err:
        sentry_sdk.metrics.incr(
            key="test_agent_orders.iteration.abandoned",
            value=1,
            tags=dict(query_string, reason=err.__class__.__name__),
        )
    except Exception as err:
        sentry_sdk.capture_exception(err)
        print(err)
