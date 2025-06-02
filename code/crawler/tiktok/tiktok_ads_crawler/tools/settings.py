from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    TIKTOK_BIZ_API_URL: str = os.getenv("TIKTOK_BIZ_API_URL")
    TIKTOK_BIZ_APP_ID: str = os.getenv("TIKTOK_BIZ_APP_ID")
    TIKTOK_BIZ_SECRET: str = os.getenv("TIKTOK_BIZ_SECRET")
    TIKTOK_BIZ_REDIRECT_URI: str = os.getenv("TIKTOK_BIZ_REDIRECT_URI")

    INSERT_SERVICE_URL: str = os.getenv("INSERT_SERVICE_URL")
    CONNECTOR_CALLBACK_URL: str = os.getenv("CONNECTOR_CALLBACK_URL")

settings = Settings()
