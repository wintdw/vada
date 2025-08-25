import os
from pathlib import Path

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str = ""  # Optional for Docker
    INSERT_SERVICE_BASEURL: str

    SHOPEE_PARTNER_ID: int
    SHOPEE_PARTNER_KEY_FILE: str = ""
    # SHOPEE_PARTNER_KEY: str = ""
    
    @property
    def SHOPEE_PARTNER_KEY(self) -> str:
        if self.SHOPEE_PARTNER_KEY_FILE and os.path.isfile(self.SHOPEE_PARTNER_KEY_FILE):
            with open(self.SHOPEE_PARTNER_KEY_FILE, "r") as file:
                return file.read().strip()
        else:
            raise ValueError("SHOPEE_PARTNER_KEY_FILE is not set or file does not exist.")
    
    API_BASE_URL: str
    
    SHOPEE_SHOP_AUTH_CALLBACK: str
    
    # New environment variables for different domains
    SHOPEE_API_DOMAIN: str = "partner.shopeemobile.com"
    SHOPEE_AUTH_DOMAIN: str = "partner.shopeemobile.com"

    class Config:
        # Load .env.local first (highest priority), then .env as fallback
        env_file = [".env.local", ".env"]
        env_file_encoding = 'utf-8'

    @property
    def MYSQL_PASSWD(self) -> str:
        if self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                return file.read().strip()
        else:
            raise ValueError("MYSQL_PASSWD_FILE is not set or file does not exist.")
        
settings = Settings()
