import json, os
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.serverless import serverless_function
from datetime import datetime, timezone
from contextlib import contextmanager


sentry_sdk.init(
    dsn=os.environ.get("PYTHON_LAMBDA_SENTRY_DSN"),
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    integrations=[
        AwsLambdaIntegration(timeout_warning=True),
    ],
)

@contextmanager
def sentry_trace(headers, body, latency):
    """
    A context manager to start/continue a Sentry transaction and span.
    Yields the open Sentry span so that the caller can add additional data
    or perform operations within the traced context.
    """
    # Continue the trace from incoming headers
    transaction = sentry_sdk.continue_trace(
        headers,
        op="function",
        name="distribution-allocator-consumer-transaction",
    )
    with sentry_sdk.start_transaction(transaction):
        with sentry_sdk.start_span(op="queue.process", name="queue_consumer") as span:
            try:
                # Set relevant data for debugging & observability
                span.set_data("messaging.message.id", body.get("MessageId"))
                span.set_data("messaging.destination.name", "plant-inventory-updated")
                span.set_data("messaging.message.body.size", len(body))
                span.set_data("messaging.message.receive.latency", latency)
                # Yield control back to the caller while the span is active
                yield span
            except Exception as e:
                # Capture the exception and attach it to the span
                span.set_status("internal_error")
                span.set_data("error", str(e))
                sentry_sdk.capture_exception(e)
                raise  # Re-raise the exception after capturing it

def process_latency(body):
    timestamp_str = body.get("Timestamp")  # e.g., "2025-01-30T01:04:23.860Z"
    if not timestamp_str:
        return None

    # Convert Z to +00:00 for proper ISO parsing
    timestamp_str = timestamp_str.replace("Z", "+00:00")
    message_time = datetime.fromisoformat(timestamp_str)  # --> datetime object in UTC

    # Current time in UTC
    now = datetime.now(timezone.utc)

    # Calculate latency
    latency = now - message_time
    return latency

@serverless_function
def lambda_handler(event, context):
    try:
        records = event["Records"]
        record_count = len(records)
        print(f"Received {record_count} records in this invocation.")

        for record in records:
            raw_body = record.get('body')
            if not raw_body:
                raise ValueError("SQS message has no body.")

            # Parse the body (SNS wrapper around your actual message)
            body = json.loads(raw_body)
            print(f"Processing message body: {body}")

            latency = process_latency(body)

            raw_message = body.get("Message")
            if not raw_message:
                raise ValueError("Message field is missing or empty.")

            # Parse the actual application message
            message = json.loads(raw_message)
            print(f"Processing message: {message}")

            headers = message.get("headers") or {}

            with sentry_trace(headers, body, latency) as span:
                try:
                    inventory_list = message.get("inventory")
                    if not isinstance(inventory_list, list):
                        raise ValueError("Inventory field is missing or not a list.")

                    for idx, quantity in enumerate(inventory_list):
                        if quantity < 0:
                            raise ValueError(
                                f"Negative inventory detected for index {idx}: {quantity}"
                            )
                    span.set_status("ok")
                except Exception as e:
                    span.set_status("internal_error")
                    # Capture the exception in Sentry
                    sentry_sdk.capture_exception(e)
                    raise  # Re-raise the exception after capturing it

        return {"statusCode": 200, "body": f"Processed {record_count} record(s)"}

    except Exception as e:
        # Capture the exception in Sentry
        sentry_sdk.capture_exception(e)
        return {"statusCode": 500, "body": str(e)}
