import asyncio
import json
import logging
import random
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

    async def create_consumer(self, topic_pattern: str, group_id: str = "default"):
        """Initialize and start a Kafka consumer."""
        if not self.consumer:
            self.consumer = AIOKafkaConsumer(
                loop=asyncio.get_event_loop(),
                bootstrap_servers=self.kafka_broker,
                group_id=group_id,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
                fetch_max_bytes=52428800,  # 50 MB
                fetch_min_bytes=1,  # Minimum bytes to fetch
                fetch_max_wait_ms=3000,  # Maximum wait time in milliseconds
                max_poll_records=1000,  # Maximum number of records returned in a single poll
                metadata_max_age_ms=20000,  # This controls the polling interval when using pattern subscriptions
            )
            await self.consumer.start()
            self.consumer.subscribe(pattern=topic_pattern)
            logging.info("Kafka consumer started")

    async def consume_message(self) -> Dict[str, Any]:
        """Consume a single message from Kafka."""
        if not self.consumer:
            logging.error("Consumer is not initialized. Call `create_consumer` first.")
            return

        message = await self.consumer.getone()
        logging.info(f"Consumed message: {message.value.decode('utf-8')}")
        return json.loads(message.value.decode("utf-8"))

    async def consume_messages(
        self, batch_size: int = 1000, timeout_ms: int = 10000
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
                bootstrap_servers=self.kafka_broker,
                enable_idempotence=True,
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

    async def produce_messages(
        self, topic: str, messages: List[Dict[str, Any]], batch_size: int = 1000
    ):
        """Produce a batch of messages to a Kafka topic."""
        if not self.producer:
            logging.error("Producer is not initialized. Call `create_producer` first.")
            return

        batch = self.producer.create_batch()
        partitions = list(await self.producer.partitions_for(topic))
        partition_count = len(partitions)
        partition_index = 0
        msg_index = 0

        while msg_index < len(messages):
            # Prepare the message as bytes
            payload = json.dumps(messages[msg_index]).encode("utf-8")

            # Append to the batch
            metadata = batch.append(key=None, value=payload, timestamp=None)

            # Batch is full or reached batch_size
            # Send the batch to Kafka, balancing across partitions
            if metadata is None or batch.record_count() >= batch_size:
                # Round-robin partition selection
                partition = partitions[partition_index % partition_count]
                await self.producer.send_batch(batch, topic, partition=partition)
                logging.info(
                    "Batch %d: %d messages sent to topic %s partition %d",
                    partition_index,
                    batch.record_count(),
                    topic,
                    partition,
                )

                # Start a new batch
                batch = self.producer.create_batch()

                # Move to the next partition for the next batch
                partition_index += 1

            msg_index += 1

        # Send any remaining messages in the batch
        if batch.record_count() > 0:
            partition = partitions[partition_index % partition_count]
            await self.producer.send_batch(batch, topic, partition=partition)
            logging.info(
                "Last batch: %d messages sent to topic %s partition %d",
                batch.record_count(),
                topic,
                partition,
            )

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
