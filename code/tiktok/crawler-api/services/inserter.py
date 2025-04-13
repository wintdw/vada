import json

from tools import post
from tools.settings import settings

async def inserter_post_data(data: dict):
    request_json = await post(
        url = f"{settings.INSERTER_URL}/jsonl",
        headers={'Content-Type': 'application/x-ndjson'},
        json_data=data
    )
    return request_json
