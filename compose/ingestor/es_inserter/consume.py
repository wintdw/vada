import logging
from confluent_kafka import Consumer


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka.ilb.vadata.vn:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dev_input")
CONSUMER = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER_URL,
        "group.id": "es_inserter_group",
        "auto.offset.reset": "earliest",
    }
)
CONSUMER.subscribe([KAFKA_TOPIC])
