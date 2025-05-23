# pylint: disable=import-error,wrong-import-position

"""
This module is for processing jsonl and pushing to ES index
"""

import logging
import asyncio
from fastapi import FastAPI  # type: ignore

from etl.insert.router import json, jsonl, health


app = FastAPI()
asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


app.include_router(health.router)
app.include_router(json.router)
app.include_router(jsonl.router)
