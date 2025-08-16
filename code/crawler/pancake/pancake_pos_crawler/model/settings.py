import os

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    APP_ENV: str

    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str

    PCP_BASE_URL: str

    INSERT_SERVICE_BASEURL: str

    @property
    def MYSQL_PASSWD(self) -> str:
        if self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                return file.read().strip()
        else:
            raise ValueError("MYSQL_PASSWD_FILE is not set or file does not exist.")


settings = Settings()
