from pydantic_settings import BaseSettings  # type: ignore
import os


class Settings(BaseSettings):
    API_BASE_URL: str | None = os.getenv("API_BASE_URL")
    INSERT_SERVICE_BASEURL: str | None = os.getenv("INSERT_SERVICE_BASEURL")
    GOOGLE_APP_SECRET_FILE: str | None = os.getenv("GOOGLE_APP_SECRET_FILE")
    GOOGLE_DEVELOPER_TOKEN: str | None = os.getenv("GOOGLE_DEVELOPER_TOKEN")
    CALLBACK_FINAL_URL: str | None = os.getenv("CALLBACK_FINAL_URL")
    MYSQL_HOST: str | None = os.getenv("MYSQL_HOST")
    MYSQL_USER: str | None = os.getenv("MYSQL_USER")
    MYSQL_DB: str | None = os.getenv("MYSQL_DB")
    MYSQL_PASSWD_FILE: str | None = os.getenv("MYSQL_PASSWD_FILE")


settings = Settings()
