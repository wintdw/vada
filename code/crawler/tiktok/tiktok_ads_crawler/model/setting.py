import os
from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str

    TIKTOK_BIZ_API_URL: str
    TIKTOK_BIZ_APP_ID: str
    TIKTOK_BIZ_SECRET: str
    TIKTOK_BIZ_REDIRECT_URI: str

    INSERT_SERVICE_URL: str
    CONNECTOR_CALLBACK_URL: str

    @property
    def MYSQL_PASSWD(self) -> str:
        if self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                return file.read().strip()
        else:
            raise ValueError("MYSQL_PASSWD_FILE is not set or file does not exist.")


settings = Settings()
