import os

from libs.async_kafka import AsyncKafkaProcessor


KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka.ilb.vadata.vn:9092")


def get_kafka_processor():
    return AsyncKafkaProcessor(KAFKA_BROKER_URL)
