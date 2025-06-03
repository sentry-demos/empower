from .email_subscribe import app
import time, random
import sentry_sdk


@app.task(bind=True, default_queue='celery-new-subscriptions')
def sendEmail(self, email):
  try:
    x = random.randrange(5)
    if x == 0:
        raise Exception("sending email error")
    time.sleep(x)
    print("Sending email to: " + email)
    return x
  except Exception as e:
      raise self.retry(exc=e, countdown=10, max_retries=5)
