# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon Simple Notification
Service (Amazon SNS) to create notification topics, add subscribers, and publish
messages.
"""

import json
import os
import logging
import random
import time
import dotenv
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
import boto3
from botocore.exceptions import ClientError
from contextlib import contextmanager

dotenv.load_dotenv()

sentry_sdk.init(
    dsn=os.environ["FLASK_APP_DSN"],
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
        AwsLambdaIntegration(),
    ],
)


logger = logging.getLogger(__name__)


# snippet-start:[python.example_code.sns.SnsWrapper]
class SnsWrapper:
    """Encapsulates Amazon SNS topic and subscription functions."""

    def __init__(self, sns_resource):
        """
        :param sns_resource: A Boto3 Amazon SNS resource.
        """
        self.sns_resource = sns_resource
        self.sns_client = boto3.client("sns")

    # snippet-end:[python.example_code.sns.SnsWrapper]

    # snippet-start:[python.example_code.sns.CreateTopic]
    def create_topic(self, name):
        """
        Creates a notification topic.

        :param name: The name of the topic to create.
        :return: The newly created topic.
        """
        try:
            topic = self.sns_resource.create_topic(Name=name)
            logger.info("Created topic %s with ARN %s.", name, topic.arn)
        except ClientError:
            logger.exception("Couldn't create topic %s.", name)
            raise
        else:
            return topic

    # snippet-end:[python.example_code.sns.CreateTopic]

    def get_existing_topic_arn(self, topic_name):
      topics = self.sns_client.list_topics()["Topics"]
      print(topics)
      for topic in topics:
          if topic_name in topic["TopicArn"]:
              return topic["TopicArn"]
      return None

    # snippet-start:[python.example_code.sns.ListTopics]
    def list_topics(self):
        """
        Lists topics for the current account.

        :return: An iterator that yields the topics.
        """
        try:
            topics_iter = self.sns_resource.topics.all()
            logger.info("Got topics.")
        except ClientError:
            logger.exception("Couldn't get topics.")
            raise
        else:
            return topics_iter

    # snippet-end:[python.example_code.sns.ListTopics]

    # snippet-start:[python.example_code.sns.DeleteTopic]
    @staticmethod
    def delete_topic(topic):
        """
        Deletes a topic. All subscriptions to the topic are also deleted.
        """
        try:
            topic.delete()
            logger.info("Deleted topic %s.", topic.arn)
        except ClientError:
            logger.exception("Couldn't delete topic %s.", topic.arn)
            raise

    # snippet-end:[python.example_code.sns.DeleteTopic]

    # snippet-start:[python.example_code.sns.Subscribe]
    @staticmethod
    def subscribe(topic, protocol, endpoint):
        """
        Subscribes an endpoint to the topic. Some endpoint types, such as email,
        must be confirmed before their subscriptions are active. When a subscription
        is not confirmed, its Amazon Resource Number (ARN) is set to
        'PendingConfirmation'.

        :param topic: The topic to subscribe to.
        :param protocol: The protocol of the endpoint, such as 'sms' or 'email'.
        :param endpoint: The endpoint that receives messages, such as a phone number
                         (in E.164 format) for SMS messages, or an email address for
                         email messages.
        :return: The newly added subscription.
        """
        try:
            subscription = topic.subscribe(
                Protocol=protocol, Endpoint=endpoint, ReturnSubscriptionArn=True
            )
            logger.info("Subscribed %s %s to topic %s.", protocol, endpoint, topic.arn)
        except ClientError:
            logger.exception(
                "Couldn't subscribe %s %s to topic %s.", protocol, endpoint, topic.arn
            )
            raise
        else:
            return subscription

    # snippet-end:[python.example_code.sns.Subscribe]

    # snippet-start:[python.example_code.sns.ListSubscriptions]
    def list_subscriptions(self, topic=None):
        """
        Lists subscriptions for the current account, optionally limited to a
        specific topic.

        :param topic: When specified, only subscriptions to this topic are returned.
        :return: An iterator that yields the subscriptions.
        """
        try:
            if topic is None:
                subs_iter = self.sns_resource.subscriptions.all()
            else:
                subs_iter = topic.subscriptions.all()
            logger.info("Got subscriptions.")
        except ClientError:
            logger.exception("Couldn't get subscriptions.")
            raise
        else:
            return subs_iter

    # snippet-end:[python.example_code.sns.ListSubscriptions]

    # snippet-start:[python.example_code.sns.SetSubscriptionAttributes]
    @staticmethod
    def add_subscription_filter(subscription, attributes):
        """
        Adds a filter policy to a subscription. A filter policy is a key and a
        list of values that are allowed. When a message is published, it must have an
        attribute that passes the filter or it will not be sent to the subscription.

        :param subscription: The subscription the filter policy is attached to.
        :param attributes: A dictionary of key-value pairs that define the filter.
        """
        try:
            att_policy = {key: [value] for key, value in attributes.items()}
            subscription.set_attributes(
                AttributeName="FilterPolicy", AttributeValue=json.dumps(att_policy)
            )
            logger.info("Added filter to subscription %s.", subscription.arn)
        except ClientError:
            logger.exception(
                "Couldn't add filter to subscription %s.", subscription.arn
            )
            raise

    # snippet-end:[python.example_code.sns.SetSubscriptionAttributes]

    # snippet-start:[python.example_code.sns.Unsubscribe]
    @staticmethod
    def delete_subscription(subscription):
        """
        Unsubscribes and deletes a subscription.
        """
        try:
            subscription.delete()
            logger.info("Deleted subscription %s.", subscription.arn)
        except ClientError:
            logger.exception("Couldn't delete subscription %s.", subscription.arn)
            raise

    # snippet-end:[python.example_code.sns.Unsubscribe]

    # snippet-start:[python.example_code.sns.Publish_TextMessage]
    def publish_text_message(self, phone_number, message):
        """
        Publishes a text message directly to a phone number without need for a
        subscription.

        :param phone_number: The phone number that receives the message. This must be
                             in E.164 format. For example, a United States phone
                             number might be +12065550101.
        :param message: The message to send.
        :return: The ID of the message.
        """
        try:
            response = self.sns_resource.meta.client.publish(
                PhoneNumber=phone_number, Message=message
            )
            message_id = response["MessageId"]
            logger.info("Published message to %s.", phone_number)
        except ClientError:
            logger.exception("Couldn't publish message to %s.", phone_number)
            raise
        else:
            return message_id

    # snippet-end:[python.example_code.sns.Publish_TextMessage]

    # snippet-start:[python.example_code.sns.Publish_MessageAttributes]
    @staticmethod
    def publish_message(topic, message, attributes):
        """
        Publishes a message, with attributes, to a topic. Subscriptions can be filtered
        based on message attributes so that a subscription receives messages only
        when specified attributes are present.

        :param topic: The topic to publish to.
        :param message: The message to publish.
        :param attributes: The key-value attributes to attach to the message. Values
                           must be either `str` or `bytes`.
        :return: The ID of the message.
        """
        try:
            att_dict = {}
            for key, value in attributes.items():
                if isinstance(value, str):
                    att_dict[key] = {"DataType": "String", "StringValue": value}
                elif isinstance(value, bytes):
                    att_dict[key] = {"DataType": "Binary", "BinaryValue": value}
            response = topic.publish(Message=message, MessageAttributes=att_dict)
            message_id = response["MessageId"]
            logger.info(
                "Published message with attributes %s to topic %s.",
                attributes,
                topic.arn,
            )
        except ClientError:
            logger.exception("Couldn't publish message to topic %s.", topic.arn)
            raise
        else:
            return message_id

    # snippet-end:[python.example_code.sns.Publish_MessageAttributes]

    def publish_message(self, topic_arn, message: dict):
      """
      Publishes a given dictionary to the SNS topic as a JSON string.

      :param message: Dictionary to publish.
      :return: Response from the SNS publish API.
      """
      # Convert the dictionary to a JSON string
      json_message = json.dumps(message)

      # Publish the message
      response = self.sns_client.publish(
          TopicArn=topic_arn,
          Message=json_message
      )
      return response

    # snippet-start:[python.example_code.sns.Publish_MessageStructure]
    @staticmethod
    def publish_multi_message(
        topic, subject, default_message, sms_message, email_message
    ):
        """
        Publishes a multi-format message to a topic. A multi-format message takes
        different forms based on the protocol of the subscriber. For example,
        an SMS subscriber might receive a short version of the message
        while an email subscriber could receive a longer version.

        :param topic: The topic to publish to.
        :param subject: The subject of the message.
        :param default_message: The default version of the message. This version is
                                sent to subscribers that have protocols that are not
                                otherwise specified in the structured message.
        :param sms_message: The version of the message sent to SMS subscribers.
        :param email_message: The version of the message sent to email subscribers.
        :return: The ID of the message.
        """
        try:
            message = {
                "default": default_message,
                "sms": sms_message,
                "email": email_message,
            }
            response = topic.publish(
                Message=json.dumps(message), Subject=subject, MessageStructure="json"
            )
            message_id = response["MessageId"]
            logger.info("Published multi-format message to topic %s.", topic.arn)
        except ClientError:
            logger.exception("Couldn't publish message to topic %s.", topic.arn)
            raise
        else:
            return message_id


# snippet-end:[python.example_code.sns.Publish_MessageStructure]

def generate_messages(num_messages=20):
    """
    Generates a list of messages with the same plantNames and inventory,
    but a random starting shipment_id that increments by 1 for each message.

    Ex.
    message = {
        'plantNames' : ["fern", "spider", "cactus"],
        'inventory' : [10, 10 , 20],
        'shipment_id' : 1234
    }
    """
    messages = []

    # Generate a random starting shipment_id (e.g., between 1000 and 9999)
    start_shipment_id = random.randint(1000, 9999)

    for i in range(num_messages):
        message = {
            'plantNames': ["fern", "spider", "cactus"],
            'inventory': [10, 10, 20],
            # Add i to keep shipment IDs sequential
            'shipment_id': start_shipment_id + i
        }
        messages.append(message)

    # Negative inv value for the recieve lambdas to throw an error to sentry
    message = {
      'plantNames': ["fern", "spider", "cactus"],
      'inventory': [-10, 10, 20],
      # Add i to keep shipment IDs sequential
      'shipment_id': 666
    }
    messages.append(message)

    return messages

@contextmanager
def sentry_trace_producer(msg):
    """
    A context manager to start a Sentry transaction and span for message publishing.
    Yields the open Sentry span so that the caller can add additional data
    or perform operations within the traced context.
    """
    with sentry_sdk.start_transaction(
        op="function",
        name="inventory-updated-producer-transaction",
    ):
        with sentry_sdk.start_span(
            op="queue.publish",
            name="queue_producer",
        ) as span:
            try:
                # Set span data
                span.set_data("messaging.message.id", msg.get('shipment_id'))
                span.set_data("messaging.destination.name", "plant-inventory-updated")
                span.set_data("messaging.message.body.size", len(msg))

                # Add trace headers to the message
                msg['headers'] = {
                    "sentry-trace": sentry_sdk.get_traceparent(),
                    "baggage": sentry_sdk.get_baggage(),
                }

                yield span
            except Exception as e:
                # Capture the exception and attach it to the span
                span.set_status("internal_error")
                span.set_data("error", str(e))
                sentry_sdk.capture_exception(e)
                raise  # Re-raise the exception after capturing it

def usage_demo():
    print("-" * 88)
    print("Welcome to the Sentry Plant Inventory Update AWS SNS/SQS/Lambda Demo!")
    print("-" * 88)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    sns_wrapper = SnsWrapper(boto3.resource("sns"))

    messages = generate_messages(20)

    print(messages[0])

    topic = sns_wrapper.get_existing_topic_arn('plant-inventory-updated')

    for msg in messages:
      with sentry_trace_producer(msg) as span:
            response = sns_wrapper.publish_message(topic, msg)
            print("Publish response:", response["MessageId"])
            span.set_status("ok")


    print("Thanks for the plants!")
    print("-" * 88)

    # throw an error to sentry, capture it with sentry_sdk
    try:
      raise Exception("This is a test error")
    except Exception as e:
      sentry_sdk.capture_exception(e)


if __name__ == "__main__":
    usage_demo()
