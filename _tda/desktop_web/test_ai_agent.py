import random
import time
from datetime import datetime

import sentry_sdk
from selenium.webdriver.common.by import By


WAIT_BEFORE_CLOSE_SECONDS = 80  # Allow time for Sentry trace capture
BASE_ITERATIONS = 3
JITTER_PERCENT = 30

LIGHT_OPTIONS = ["low light", "medium light", "full sun"]
MAINTENANCE_OPTIONS = ["yes", "no"]


def get_seasonal_multiplier() -> float:
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday()

    if 9 <= hour <= 17:
        time_multiplier = 1.1  # Business hours (peak)
    elif 18 <= hour <= 22:
        time_multiplier = 0.9  # Evening
    else:
        time_multiplier = 0.5  # Night/early morning

    if 0 <= day_of_week <= 4:
        day_multiplier = 1.2  # Weekdays
    else:
        day_multiplier = 0.7  # Weekends

    return time_multiplier * day_multiplier


def add_jitter(value: float, jitter_percent: int = JITTER_PERCENT) -> float:
    jitter_amount = (jitter_percent / 100) * value
    random_jitter = (random.random() - 0.5) * 2 * jitter_amount
    return max(0.0, value + random_jitter)


def calculate_iterations() -> int:
    seasonal_multiplier = get_seasonal_multiplier()
    raw_iterations = add_jitter(BASE_ITERATIONS * seasonal_multiplier)
    
    if raw_iterations < 1.0:
        return 1 if random.random() < raw_iterations else 0
    
    return round(raw_iterations)


def get_random_inputs() -> tuple[str, str]:
    return random.choice(LIGHT_OPTIONS), random.choice(MAINTENANCE_OPTIONS)


def run_single_chat_interaction(driver, url: str, light: str, maintenance: str, iteration: int):
    driver.get(url)
    time.sleep(3)
    
    chat_button = driver.find_element(By.ID, 'chat-widget-button')
    chat_button.click()
    time.sleep(5)  # Wait for welcome messages
    
    chat_input = driver.find_element(By.ID, 'chat-message-input')
    chat_input.send_keys(light)
    
    send_button = driver.find_element(By.ID, 'chat-send-button')
    send_button.click()
    time.sleep(3)
    
    chat_input = driver.find_element(By.ID, 'chat-message-input')
    chat_input.send_keys(maintenance)
    
    send_button = driver.find_element(By.ID, 'chat-send-button')
    send_button.click()
    
    print(f"⏳ Waiting {WAIT_BEFORE_CLOSE_SECONDS}s for trace capture...")
    time.sleep(WAIT_BEFORE_CLOSE_SECONDS)
    
    chat_button.click()
    time.sleep(5)


def test_ai_agent(desktop_web_1browser_driver, endpoints):
    url = endpoints.react_endpoint
    iterations = calculate_iterations()
    
    print(f"Starting AI Agent test with {iterations} iteration(s)")
    
    try:
        for i in range(iterations):
            light, maintenance = get_random_inputs()
            run_single_chat_interaction(
                desktop_web_1browser_driver, url, light, maintenance, i + 1
            )
    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise
