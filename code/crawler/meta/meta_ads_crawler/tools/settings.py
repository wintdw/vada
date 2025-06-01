from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    META_APP_ID: str = os.getenv("META_APP_ID")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET")
    META_GRAPH_API_URL: str = os.getenv("META_GRAPH_API_URL")
    META_REDIRECT_URI: str = os.getenv("META_REDIRECT_URI")

    CONNECTOR_CALLBACK_URL: str = os.getenv("CONNECTOR_CALLBACK_URL")
    CRAWLER_SERVICE_URL: str = os.getenv("CRAWLER_SERVICE_URL")

settings = Settings()
