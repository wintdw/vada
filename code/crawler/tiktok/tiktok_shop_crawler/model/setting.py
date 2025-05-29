import os

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str

    INSERT_SERVICE_URL: str

    TIKTOK_SHOP_APP_KEY: str
    TIKTOK_SHOP_APP_SECRET_FILE: str
    TIKTOK_SHOP_AUTH_BASEURL: str

    @property
    def TIKTOK_SHOP_APP_SECRET(self) -> str:
        with open(self.TIKTOK_SHOP_APP_SECRET_FILE, "r") as f:
            return f.read().strip()

    @property
    def MYSQL_PASSWD(self) -> str:
        if self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                return file.read().strip()
        return ""


settings = Settings()
