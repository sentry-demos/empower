import time
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def test_clock_drift(desktop_web_driver, endpoints, batch_size, backend, random, sleep_length, cexp):

    desktop_web_driver.get("https://time.gov")
    time.sleep(5)
    # scroll down
    desktop_web_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(20)


