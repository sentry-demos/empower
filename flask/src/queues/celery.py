from celery import Celery, signals
import sentry_sdk, os, dotenv
import os

dotenv.load_dotenv()

redis_host = os.environ.get("REDISHOST", "localhost")
redis_port = int(os.environ.get("REDISPORT"))

redis_url = f"redis://{redis_host}:{redis_port}/1"

app = Celery('subscribe',
             broker=redis_url,
             backend=redis_url,
             include=['src.queues.tasks'],
             broker_connection_retry_on_startup=True)

# Initialize Sentry SDK on Celery startup
@signals.celeryd_init.connect
def init_sentry(**_kwargs):
    dotenv.load_dotenv()
    RELEASE = os.environ["RELEASE"]
    DSN = os.environ["FLASK_APP_DSN"]
    ENVIRONMENT = os.environ["FLASK_ENV"]
    sentry_sdk.init(
        dsn=DSN,
        release=RELEASE,
        environment=ENVIRONMENT,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

if __name__ == '__main__':
    app.start()
