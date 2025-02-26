from .email_subscribe import app
import time, random
import sentry_sdk


@app.task(bind=True)
def sendEmail(self, email):
    try:
      # Create the span
      with sentry_sdk.start_span(
          op="queue.process",
          name="queue_consumer",
      ) as span:
        span.set_data("messaging.destination.name", 'email_subscribe')
        x = random.randrange(5)
        if x == 0:
          raise Exception("sending email error")
        time.sleep(x)
        print("Sending email to: " + email)
        return x
    except Exception as e:
      with sentry_sdk.start_transaction(name="src.queues.retry"):
        with sentry_sdk.start_span(
            op="queue.publish",
            name="queue_producer",
        ) as span:
          span.set_data("messaging.destination.name", 'email_subscribe')
          raise self.retry(exc=e, countdown=30, max_retries=5)

