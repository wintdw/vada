import os

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str

    INSERT_SERVICE_BASEURL: str


    SHOPEE_PARTNER_ID: int
    SHOPEE_PARTNER_KEY: str
    API_BASE_URL: str
    
    SHOPEE_AUTH_BASEURL: str
    SHOPEE_AUTH_LINK: str
    SHOPEE_SHOP_AUTH_CALLBACK: str
    SHOPEE_OPEN_API_BASEURL: str

    @property
    def MYSQL_PASSWD(self) -> str:
        if self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                return file.read().strip()
        else:
            raise ValueError("MYSQL_PASSWD_FILE is not set or file does not exist.")

settings = Settings()
