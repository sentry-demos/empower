import sentry_sdk
from sentry_sdk.crons import monitor
import random
import urllib.request
import time
import dotenv
import os

dotenv.load_dotenv()

# set in ../env-config/*.env
DSN = os.environ["CRONSPYTHON_DSN"]
MONITOR_SLUG = os.environ["CRONSPYTHON_MONITOR_SLUG"]
FAILURE_PERCENT_CHANCE = 5 
STUCK_PERCENT_CHANCE = 5 
STUCK_SLEEP_MIN_MINUTES = 6
STUCK_SLEEP_MAX_MINUTES = 20

random_number = random.randint(0, 99)

@monitor(monitor_slug=MONITOR_SLUG)
def job():
    if random_number < FAILURE_PERCENT_CHANCE:
        print("Attempting to call an API that is down.")
        urllib.request.urlopen("https://my-api-endpoint.demo-service.com/v1/list")
        # Process the response as needed
    elif random_number < (FAILURE_PERCENT_CHANCE + STUCK_PERCENT_CHANCE):
        print("Stuck (sleeping from 6 to 20 minutes).")
        sleep_duration = random.randint(STUCK_SLEEP_MIN_MINUTES * 60, STUCK_SLEEP_MAX_MINUTES * 60)
        time.sleep(sleep_duration)
    else:
        print("Success.")

if __name__ == "__main__":
    sentry_sdk.init(dsn=DSN)
    sentry_sdk.set_context("monitor", {
        "slug": MONITOR_SLUG,
    })
    job()
    exit(0)
