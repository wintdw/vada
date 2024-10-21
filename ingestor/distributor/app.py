import json
import logging
import aiohttp
from confluent_kafka import Consumer, Producer
from typing import Dict


KAFKA_BROKER_URL = "kafka.ilb.vadata.vn:9092"
KAFKA_INPUT_TOPIC = "dev_input"
KAFKA_OUTPUT_TOPIC = "dev_output"
IMS_ENDPOINT = "http://your-http-endpoint.com/api"

logging.basicConfig(level=logging.INFO)


CONSUMER = Consumer({
    'bootstrap.servers': KAFKA_BROKER_URL,
    'group.id': 'dev_distributor_group',
    'auto.offset.reset': 'earliest'
})

PRODUCER = Producer({
    'bootstrap.servers': KAFKA_BROKER_URL
})

# Flow: consume -> process -> produce -> to index-management-service
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

def delivery_report(err, msg):
    """ Callback function called once the message is delivered or fails """
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_msg(producer: Producer, topic: str, json_msg: Dict):
    # only produce non-empty message
    if json_msg:
        producer.produce(
            topic,
            value=json.dumps(json_msg).encode('utf-8'),
            callback=delivery_report
        )

async def to_ims(msg: Dict) -> Dict:
    """
    Send a JSON message to the IMS HTTP endpoint asynchronously.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(IMS_ENDPOINT, json=msg) as response:
                response.raise_for_status()  # Raise an error for bad responses
                logging.info(f"Message sent to IMS: {msg}, Response: {response.status}")
                return {"status": "success"}
        except aiohttp.ClientResponseError as e:
            error_message = await e.text()
            logging.error(f"HTTP error occurred: {e.status} - {error_message}")
            return {"status": "error", "error": error_message}
        except Exception as e:
            logging.error(f"An error occurred while sending to IMS: {str(e)}")
            return {"status": "error", "error": str(e)}


CONSUMER.subscribe([KAFKA_INPUT_TOPIC])

# Main service loop
try:
    while True:
        input_msg = consume_msg(CONSUMER)
        output_msg = process_msg(input_msg)

        produce_msg(PRODUCER, KAFKA_OUTPUT_TOPIC, output_msg)

        # waiting for the IMS
        #await to_ims(output_msg)

        # Flush the producer to ensure messages are sent
        PRODUCER.flush()

except KeyboardInterrupt:
    pass
finally:
    # Clean up
    consumer.close()
