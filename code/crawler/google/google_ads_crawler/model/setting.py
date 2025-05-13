from pydantic_settings import BaseSettings  # type: ignore
import os


class Settings(BaseSettings):
    INSERT_SERVICE_BASEURL: str = os.getenv("INSERT_SERVICE_BASEURL")
    GOOGLE_APP_SECRET_FILE: str = os.getenv("GOOGLE_APP_SECRET_FILE")
    GOOGLE_DEVELOPER_TOKEN: str = os.getenv("GOOGLE_DEVELOPER_TOKEN")
    CALLBACK_FINAL_URL: str = os.getenv("CALLBACK_FINAL_URL")


settings = Settings()
