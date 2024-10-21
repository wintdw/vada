import json
import logging
from confluent_kafka import Consumer, Producer
from typing import Dict


KAFKA_BROKER_URL = "kafka.ilb.vadata.vn:9092"
KAFKA_INPUT_TOPIC = "dev_input"
KAFKA_OUTPUT_TOPIC = "dev_output"

logging.basicConfig(level=logging.INFO)


CONSUMER = Consumer({
    'bootstrap.servers': KAFKA_BROKER_URL,
    'group.id': 'dev_distributor_group',
    'auto.offset.reset': 'earliest'
})

PRODUCER = Producer({
    'bootstrap.servers': KAFKA_BROKER_URL
})

# Flow: consume -> process -> produce
def consume_msg(consumer: Consumer, poll_timeout: float = 3.0) -> Dict:
    msg = consumer.poll(poll_timeout)

    if msg is None:
        return {}

    return json.loads(msg.value().decode('utf-8'))

def process_msg(msg: Dict) -> Dict:
    """
    Placeholder for processing the message.
    Currently does nothing and just returns the input.
    """
    return msg

def produce_msg(producer: Producer, topic: str, json_msg: Dict):
    # only produce non-empty message
    if json_msg:
        producer.produce(
            topic,
            value=json.dumps(json_msg).encode('utf-8'),
            callback=delivery_report
        )


def delivery_report(err, msg):
    """ Callback function called once the message is delivered or fails """
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


consumer.subscribe([KAFKA_INPUT_TOPIC])

# Main service loop
try:
    while True:
        json_msg = consume_msg(CONSUMER)
        produce_msg(PRODUCER, KAFKA_OUTPUT_TOPIC, process_msg(json_msg))

        # Flush the producer to ensure messages are sent
        producer.flush()

except KeyboardInterrupt:
    pass
finally:
    # Clean up
    consumer.close()
