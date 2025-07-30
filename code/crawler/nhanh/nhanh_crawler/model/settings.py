import os

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str

    NHANH_APP_ID: str
    NHANH_BASE_URL: str
    NHANH_RETURN_LINK: str
    NHANH_SECRET_KEY_FILE: str

    INSERT_SERVICE_URL: str
    CONNECTOR_CALLBACK_URL: str

    @property
    def NHANH_SECRET_KEY(self) -> str:
        if self.NHANH_SECRET_KEY_FILE and os.path.isfile(self.NHANH_SECRET_KEY_FILE):
            with open(self.NHANH_SECRET_KEY_FILE, "r") as f:
                return f.read().strip()
        else:
            raise ValueError("NHANH_SECRET_KEY_FILE is not set or file does not exist.")

    @property
    def MYSQL_PASSWD(self) -> str:
        if self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                return file.read().strip()
        else:
            raise ValueError("MYSQL_PASSWD_FILE is not set or file does not exist.")


settings = Settings()
