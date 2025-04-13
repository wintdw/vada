from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    TIKTOK_BIZ_API_URL: str = os.getenv("TIKTOK_BIZ_API_URL")
    TIKTOK_BIZ_ACCESS_TOKEN: str = os.getenv("TIKTOK_BIZ_ACCESS_TOKEN")
    TIKTOK_BIZ_APP_ID: str = os.getenv("TIKTOK_BIZ_APP_ID")
    TIKTOK_BIZ_SECRET: str = os.getenv("TIKTOK_BIZ_SECRET")
    INSERTER_URL: str = os.getenv("INSERTER_URL")

settings = Settings()
