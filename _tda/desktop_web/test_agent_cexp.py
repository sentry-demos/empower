import random
import time
from urllib.parse import urlencode

import pytest
import sentry_sdk
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import CExp, scale_batch_size_phase

# Drives the conversational agent on the home page, the flow described in
# agent/AGENT_CRITICAL_EXPERIENCE_PLAN.md. test_ai_agent.py still drives the
# floating chat popup and is left alone.
#
# The whole point of this file is one correlation: when the products API is
# degraded, engagement with the agent falls. It shares the `cexp` fixture with
# test_cexp_checkout.py rather than having its own schedule, so the products
# API is slow for the chat and the products page in the same window — one
# backend, one incident, visible from two directions.
#
#   CHECKOUT_SUCCESS         full conversation, purchase succeeds
#   PRODUCTS_EXTREMELY_SLOW  ask for products, wait, give up   <- dropoff
#   PRODUCTS_BE_ERROR        never start the conversation      <- dropoff
#   everything else          full conversation, purchase 500s
#
# There is no coupon turn. The only seeded promo code is expired, so attempting
# one would put a guaranteed error in the healthy baseline the correlation is
# measured against.

# Below test_ai_agent.py's 0.185, which is already there "to reduce token
# usage". A completed run here is four turns against that file's two, and each
# turn is three LLM calls.
VOLUME_FACTOR = 0.9
BASE_ITERATIONS = 3
JITTER_PERCENT = 30

# test_ai_agent.py and test_basic_checkout.py both fill in on the +12 phase.
# A third competitor there starves one of them, so this one sits a quarter of a
# day away from both.
PHASE_OFFSET_HOURS = 6

# The products turn is an LLM round trip on top of flask's slow profile, and
# the degraded profile alone is 24s server-side. Generous on purpose: timing
# out here would look like a dropoff and pollute the signal being measured.
PRODUCTS_TIMEOUT = 150
TURN_TIMEOUT = 90

# Seconds to leave the trace open before navigating away, so Sentry's browser
# SDK flushes the session span.
TRACE_FLUSH_SECONDS = 12


def add_jitter(value, jitter_percent=JITTER_PERCENT):
    jitter_amount = (jitter_percent / 100) * value
    return max(0.0, value + (random.random() - 0.5) * 2 * jitter_amount)


def calculate_iterations():
    raw = VOLUME_FACTOR * add_jitter(BASE_ITERATIONS)
    if raw < 1.0:
        return 1 if random.random() < raw else 0
    return round(raw)


def _abandon(query_string, stage, reason):
    """Record that the customer stopped engaging, and why."""
    sentry_sdk.metrics.incr(
        key="test_agent_cexp.conversation.abandoned",
        value=1,
        tags=dict(query_string, stage=stage, reason=reason),
    )
    print(f"  abandoned at {stage} ({reason})")


def _click(driver, element_id, timeout=TURN_TIMEOUT):
    """Wait for an element to be clickable, then click it.

    Explicit waits rather than the global 10s implicit one: a turn is an LLM
    round trip, and the products turn can take well over a minute when the
    backend is in its degraded profile.
    """
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, element_id))
    )
    element.click()
    return element


def _wait_for_card(driver, css_selector, timeout=TURN_TIMEOUT):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


# Skip before the Sauce session is created. Like test_ai_agent.py this file has
# no batch loop, so we only coin-flip whether to run this round.
@pytest.fixture(autouse=True)
def _skip_when_off_phase(random):
    if scale_batch_size_phase(1, random, PHASE_OFFSET_HOURS) == 0:
        pytest.skip("not running this round — off-phase for this test")


def test_agent_cexp(desktop_web_1browser_driver, endpoints, sleep_length, cexp):
    driver = desktop_web_1browser_driver
    iterations = calculate_iterations()
    print(f"Starting agent cexp test with {iterations} iteration(s)")

    for i in range(iterations):
        ce = cexp()
        sentry_sdk.set_tag("cexp", ce)

        # flask is the only backend the agent's tools talk to.
        query_string = {"backend": "flask", "cexp": ce}
        # The widget only mounts on Home, so this is the site root, not /products.
        url = endpoints.react_endpoint + "?" + urlencode(query_string)

        sentry_sdk.metrics.incr(
            key="test_agent_cexp.iteration.started", value=1, tags=query_string
        )

        try:
            driver.get(url)

            # The products API is returning 500s. The customer never engages the
            # agent at all, so this window has no conversations rather than
            # failed ones.
            if ce == CExp.PRODUCTS_BE_ERROR:
                time.sleep(sleep_length())
                _abandon(query_string, "before_open", "products_be_error")
                continue

            _click(driver, "home-ask-agent")
            time.sleep(sleep_length())

            # Turn 1 — find products. This is the call that carries the latency.
            _click(driver, "chat-pill-show-products")
            try:
                _wait_for_card(driver, ".chat-product", timeout=PRODUCTS_TIMEOUT)
            except TimeoutException:
                _abandon(query_string, "products", "timeout")
                continue

            # Waited out the slow response, saw the products, and gave up
            # anyway. Leaving before the response would mean the latency never
            # got recorded, which is the thing being correlated against.
            if ce == CExp.PRODUCTS_EXTREMELY_SLOW:
                time.sleep(sleep_length())
                _abandon(query_string, "products", "products_extremely_slow")
                continue

            # Turn 2 — add everything to the cart.
            time.sleep(sleep_length())
            _click(driver, "chat-pill-add-all")
            _wait_for_card(driver, "#chat-cart")

            # Turn 3 — checkout, which renders the prefilled form.
            time.sleep(sleep_length())
            _click(driver, "chat-pill-checkout")
            _wait_for_card(driver, "#chat-checkout")

            # Turn 4 — buy. Succeeds under checkout_success, 500s otherwise,
            # matching what the site's own checkout does in the same window.
            time.sleep(sleep_length())
            _click(driver, "chat-pill-purchase")
            _wait_for_card(driver, "#chat-confirmation, #chat-error")

            sentry_sdk.metrics.incr(
                key="test_agent_cexp.iteration.completed", value=1, tags=query_string
            )

            time.sleep(TRACE_FLUSH_SECONDS)

        except (NoSuchElementException, TimeoutException) as err:
            _abandon(query_string, "unknown", err.__class__.__name__)
        except Exception as err:
            sentry_sdk.metrics.incr(
                key="test_agent_cexp.iteration.abandoned",
                value=1,
                tags=dict(query_string, stage="unknown", reason=f"other({err.__class__.__name__})"),
            )
            sentry_sdk.capture_exception(err)
            print(err)

        time.sleep(sleep_length())
