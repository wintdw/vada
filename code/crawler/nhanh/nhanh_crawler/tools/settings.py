from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    NHANH_OAUTH_VERSION: str = os.getenv("NHANH_OAUTH_VERSION")
    NHANH_APP_ID: str = os.getenv("NHANH_APP_ID")
    NHANH_RETURN_LINK: str = os.getenv("NHANH_RETURN_LINK")
    NHANH_SECRET_KEY_FILE: str = os.getenv("NHANH_SECRET_KEY_FILE")
    
    INSERT_SERVICE_URL: str = os.getenv("INSERT_SERVICE_URL")
    CONNECTOR_CALLBACK_URL: str = os.getenv("CONNECTOR_CALLBACK_URL")

settings = Settings()
