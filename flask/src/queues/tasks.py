from .celery import app
import time, random


@app.task(bind=True)
def sendEmail(self, email):
  try:
    x = random.randrange(5)
    if x == 0:
      raise Exception("sending email error")
    time.sleep(x)
    print("Sending email to: " + email)
    return x
  except Exception as e:
    raise self.retry(exc=e, countdown=300, max_retries=5)

