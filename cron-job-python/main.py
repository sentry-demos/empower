import sentry_sdk
from sentry_sdk.crons import monitor
import random
import urllib.request
import time

# cron-job-python
DSN = "https://5c0f7b0814074657819c61bee198d316@o87286.ingest.sentry.io/4505197623705600"
FAILURE_PERCENT_CHANCE = 10
STUCK_PERCENT_CHANCE = 10
STUCK_SLEEP_MIN_MINUTES = 6
STUCK_SLEEP_MAX_MINUTES = 20

random_number = random.randint(0, 99)

@monitor(monitor_slug='cron-job-monitor-python')
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
        "slug": "cron-job-monitor-python",
    })
    job()
    exit(0)
