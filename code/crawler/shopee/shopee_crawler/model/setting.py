import os

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD: str

    INSERT_SERVICE_BASEURL: str


    SHOPEE_PARTNER_ID: int
    SHOPEE_PARTNER_KEY: str
    
    
    SHOPEE_AUTH_BASEURL: str
    SHOPEE_AUTH_LINK: str
    SHOPEE_SHOP_AUTH_CALLBACK: str
    SHOPEE_OPEN_API_BASEURL: str

settings = Settings()
