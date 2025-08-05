import os

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    APP_ENV: str

    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str

    API_BASE_URL: str
    INSERT_SERVICE_BASEURL: str
    GOOGLE_APP_SECRET_FILE: str
    GOOGLE_DEVELOPER_TOKEN: str
    CALLBACK_FINAL_URL: str

    @property
    def MYSQL_PASSWD(self) -> str:
        if self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                return file.read().strip()
        return ""


settings = Settings()
