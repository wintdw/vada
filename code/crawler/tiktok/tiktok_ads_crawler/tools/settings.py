from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    TIKTOK_BIZ_API_URL: str = os.getenv("TIKTOK_BIZ_API_URL")
    TIKTOK_BIZ_APP_ID: str = os.getenv("TIKTOK_BIZ_APP_ID")
    TIKTOK_BIZ_SECRET: str = os.getenv("TIKTOK_BIZ_SECRET")
    FACEBOOK_APP_ID: str = os.getenv("FACEBOOK_APP_ID")
    FACEBOOK_APP_SECRET: str = os.getenv("FACEBOOK_APP_SECRET")
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN")
    INSERT_SERVICE_URL: str = os.getenv("INSERT_SERVICE_URL")

settings = Settings()
