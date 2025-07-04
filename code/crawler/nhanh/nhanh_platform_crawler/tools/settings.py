from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    NHANH_REDIRECT_URI: str = os.getenv("NHANH_REDIRECT_URI")
    INSERT_SERVICE_URL: str = os.getenv("INSERT_SERVICE_URL")
    CONNECTOR_CALLBACK_URL: str = os.getenv("CONNECTOR_CALLBACK_URL")

settings = Settings()
