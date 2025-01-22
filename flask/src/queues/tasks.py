from .celery import app
import time, random


@app.task
def sendEmail(email):
    time.sleep(random.randrange(5))
    print("Sending email to: " + email)
    raise Exception("sending email error")

