import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer  # type: ignore


class AsyncKafkaProcessor:
    def __init__(self, kafka_broker: str):
        """
        Initialize the Kafka processor.

        Args:
            kafka_broker (str): Kafka broker address (e.g., 'localhost:9092').
        """
        self.kafka_broker = kafka_broker
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None

    async def create_consumer(self, topic: str, group_id: str = "default"):
        """Initialize and start a Kafka consumer."""
        if not self.consumer:
            self.consumer = AIOKafkaConsumer(
                topic,
                loop=asyncio.get_event_loop(),
                bootstrap_servers=self.kafka_broker,
                group_id=group_id,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
            )
            await self.consumer.start()
            logging.info(f"Kafka consumer started for topic: {topic}")

    async def consume_message(self) -> Dict[str, Any]:
        """Consume a single message from Kafka."""
        if not self.consumer:
            logging.error("Consumer is not initialized. Call `create_consumer` first.")
            return

        message = await self.consumer.getone()
        logging.info(f"Consumed message: {message.value.decode('utf-8')}")
        return json.loads(message.value.decode("utf-8"))

    async def consume_messages(
        self, batch_size: int = 10, timeout_ms: int = 1000
    ) -> List[Dict[str, Any]]:
        """Consume a batch of messages from Kafka."""
        if not self.consumer:
            logging.error("Consumer is not initialized. Call `create_consumer` first.")
            return None

        consumed_messages = []
        data = await self.consumer.getmany(
            max_records=batch_size, timeout_ms=timeout_ms
        )
        for _, msgs in data.items():
            logging.info("Consumed %s messages", len(msgs))
            consumed_messages.extend(
                [
                    json.loads(decoded_message)
                    for decoded_message in (
                        message.value.decode("utf-8") for message in msgs
                    )
                ]
            )
            if len(consumed_messages) >= batch_size:
                return consumed_messages

        return consumed_messages

    async def create_producer(self):
        """Initialize and start a Kafka producer."""
        if not self.producer:
            self.producer = AIOKafkaProducer(
                loop=asyncio.get_event_loop(),
                bootstrap_servers=self.kafka_broker,
            )
            await self.producer.start()
            logging.info("Kafka producer started.")

    async def produce_message(self, topic: str, message: Dict[str, Any]):
        """Produce a message to a Kafka topic."""
        if not self.producer:
            logging.error("Producer is not initialized. Call `create_producer` first.")
            return

        payload = json.dumps(message).encode("utf-8")
        await self.producer.send_and_wait(topic, payload)
        logging.info(f"Produced message to topic '{topic}': {message}")

    async def close(self):
        """Stop both the consumer and producer."""
        if self.consumer:
            await self.consumer.stop()
            logging.info("Kafka consumer stopped.")
            self.consumer = None
        if self.producer:
            await self.producer.stop()
            logging.info("Kafka producer stopped.")
            self.producer = None
