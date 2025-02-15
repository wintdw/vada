import pytest
import logging
from typing import List, Dict, Any
from libs.connectors.async_kafka import AsyncKafkaProcessor

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
async def test_produce_messages():
    kafka_broker = "kafka.ilb.vadata.vn:9092"
    kafka_processor = AsyncKafkaProcessor(kafka_broker)
    await kafka_processor.create_producer()

    topic = "dw"
    msg_cnt = 100
    partition_cnt = 12
    messages: List[Dict[str, Any]] = [{"key": f"value{i}"} for i in range(1, msg_cnt)]
    batch_size = msg_cnt // partition_cnt

    await kafka_processor.produce_messages(topic, messages, batch_size)
    await kafka_processor.close()
