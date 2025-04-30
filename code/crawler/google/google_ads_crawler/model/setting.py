from pydantic_settings import BaseSettings  # type: ignore
import os


class Settings(BaseSettings):
    INSERT_SERVICE_BASEURL: str = os.getenv("INSERT_SERVICE_BASEURL")


settings = Settings()
