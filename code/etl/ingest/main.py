import logging
import asyncio
from fastapi import FastAPI  # type: ignore

from etl.ingest.router import json, health


app = FastAPI()
# asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
set_mappings_lock = asyncio.Lock()

app.include_router(health.router)
app.include_router(json.router)
