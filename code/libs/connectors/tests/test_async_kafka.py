import pytest
from typing import List, Dict, Any
from libs.connectors.async_kafka import AsyncKafkaProcessor


@pytest.fixture
async def kafka_processor():
    kafka_broker = "kafka.ilb.vadata.vn:9092"
    processor = AsyncKafkaProcessor(kafka_broker)
    await processor.create_producer()
    yield processor
    await processor.close()


@pytest.mark.asyncio
async def test_produce_messages(kafka_processor: AsyncKafkaProcessor):
    topic = "dw"
    messages: List[Dict[str, Any]] = [{"key": f"value{i}"} for i in range(1, 13)]
    batch_size = 10

    await kafka_processor.produce_messages(topic, messages, batch_size)
