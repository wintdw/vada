from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    TIKTOK_BIZ_API_URL: str = os.getenv("TIKTOK_BIZ_API_URL")
    TIKTOK_BIZ_APP_ID: str = os.getenv("TIKTOK_BIZ_APP_ID")
    TIKTOK_BIZ_SECRET: str = os.getenv("TIKTOK_BIZ_SECRET")
    TIKTOK_BIZ_REDIRECT_URI: str = os.getenv("TIKTOK_BIZ_REDIRECT_URI")

    FACEBOOK_APP_ID: str = os.getenv("FACEBOOK_APP_ID")
    FACEBOOK_APP_SECRET: str = os.getenv("FACEBOOK_APP_SECRET")
    FACEBOOK_GRAPH_API_URL: str = os.getenv("FACEBOOK_GRAPH_API_URL")
    FACEBOOK_REDIRECT_URI: str = os.getenv("FACEBOOK_REDIRECT_URI")

    INSERT_SERVICE_URL: str = os.getenv("INSERT_SERVICE_URL")
    CONNECTOR_CALLBACK_URL: str = os.getenv("CONNECTOR_CALLBACK_URL")
    MAPPINGS_BASE_URL: str = os.getenv("MAPPINGS_BASE_URL")
    CRAWLER_SERVICE_URL: str = os.getenv("CRAWLER_SERVICE_URL")

settings = Settings()
