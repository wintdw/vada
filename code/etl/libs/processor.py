import os

from etl.ingest.model.setting import settings

from libs.connectors.async_es import AsyncESProcessor

# Passwd
elastic_passwd_file = settings.ELASTIC_PASSWD_FILE
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r", encoding="utf-8") as file:
        ELASTIC_PASSWD = file.read().strip()


def get_es_processor() -> AsyncESProcessor:
    return AsyncESProcessor(settings.ELASTIC_URL, settings.ELASTIC_USER, ELASTIC_PASSWD)
