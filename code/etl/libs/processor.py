import os

from libs.connectors.async_es import AsyncESProcessor
from libs.connectors.async_kafka import AsyncKafkaProcessor
from libs.connectors.mappings import MappingsClient

ELASTIC_URL = os.getenv("ELASTIC_URL")
ELASTIC_USER = os.getenv("ELASTIC_USER")
ELASTIC_PASSWD = os.getenv("ELASTIC_PASSWD")
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r", encoding="utf-8") as file:
        ELASTIC_PASSWD = file.read().strip()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
MAPPINGS_BASEURL = os.getenv("MAPPINGS_BASEURL")


def get_es_processor() -> AsyncESProcessor:
    return AsyncESProcessor(ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD)


def get_kafka_processor() -> AsyncKafkaProcessor:
    return AsyncKafkaProcessor(KAFKA_BROKER_URL)


def get_mappings_client() -> MappingsClient:
    return MappingsClient(MAPPINGS_BASEURL)
