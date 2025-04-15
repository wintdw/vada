import json

from tools import post
from tools.settings import settings


async def send_to_insert_service(data: dict):
    request_json = await post(url=f"{settings.INSERT_SERVICE_URL}/json", json_data=data)
    return request_json
