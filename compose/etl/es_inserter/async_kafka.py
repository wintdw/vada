import json
import logging
from typing import Dict
from aiokafka import AIOKafkaConsumer
import asyncio


class AsyncKafkaProcessor:
    def __init__(
        self, kafka_broker: str, kafka_topic: str, kafka_group_id: str = "default"
    ):
        self.kafka_broker = kafka_broker
        self.kafka_topic = kafka_topic
        self.kafka_group_id = kafka_group_id
        self.consumer = None

    async def _create_consumer(self):
        """Create and start a Kafka consumer."""
        if not self.consumer:
            self.consumer = AIOKafkaConsumer(
                self.kafka_topic,
                loop=asyncio.get_event_loop(),
                bootstrap_servers=self.kafka_broker,
                group_id=self.kafka_group_id,
            )
            await self.consumer.start()
            logging.info(f"Kafka consumer started for topic: {self.kafka_topic}")

    async def consume_msg(self) -> Dict:
        """Consume a message from Kafka."""
        await self._create_consumer()

        try:
            # Consume a message
            msg_obj = await self.consumer.getone()
            if not msg_obj:
                return {}

            msg = msg_obj.value.decode("utf-8")
            logging.info(f"Consumed message: {msg}")

            return json.loads(msg)
        except Exception as e:
            logging.error(f"Error consuming message: {str(e)}")
            return {}

    def process_msg(self, msg: Dict) -> Dict:
        """Process the message."""
        # Placeholder processing function - can be customized for business logic
        return msg

    async def close_consumer(self):
        """Close the Kafka consumer."""
        if self.consumer:
            await self.consumer.stop()
            logging.info("Kafka consumer stopped.")
