from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    INSERT_SERVICE_URL: str = os.getenv("INSERT_SERVICE_URL")
    CONNECTOR_CALLBACK_URL: str = os.getenv("CONNECTOR_CALLBACK_URL")

settings = Settings()
