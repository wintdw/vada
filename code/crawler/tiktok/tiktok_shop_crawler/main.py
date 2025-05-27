import logging
from fastapi import FastAPI  # type: ignore

from model.setting import settings


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Tiktok Shop Crawler")
