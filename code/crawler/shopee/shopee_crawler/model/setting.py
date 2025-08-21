import os
from pathlib import Path

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str = ""  # Optional for Docker
    MYSQL_PASSWORD: str = ""  # Direct password for local

    INSERT_SERVICE_BASEURL: str

    SHOPEE_PARTNER_ID: int
    SHOPEE_PARTNER_KEY_FILE: str = ""
    SHOPEE_PARTNER_KEY: str = ""
    @property
    def partner_key(self) -> str:
        if self.SHOPEE_PARTNER_KEY:
            return self.SHOPEE_PARTNER_KEY
        elif self.SHOPEE_PARTNER_KEY_FILE and os.path.exists(self.SHOPEE_PARTNER_KEY_FILE):
            with open(self.SHOPEE_PARTNER_KEY_FILE, "r") as f:
                self.SHOPEE_PARTNER_KEY = f.read().strip()
            return self.SHOPEE_PARTNER_KEY
        else:
            raise ValueError("Shopee partner key not found. Set SHOPEE_PARTNER_KEY env or SHOPEE_PARTNER_KEY_FILE.")
    API_BASE_URL: str
    
    SHOPEE_SHOP_AUTH_CALLBACK: str
    
    # New environment variables for different domains
    SHOPEE_PRODUCTION_API_DOMAIN: str = "partner.shopeemobile.com"
    SHOPEE_SANDBOX_API_DOMAIN: str = "partner.shopeemobile.com"
    SHOPEE_PRODUCTION_AUTH_DOMAIN: str = "partner.shopeemobile.com"
    SHOPEE_SANDBOX_AUTH_DOMAIN: str = "partner.shopeemobile.com"

    class Config:
        # Load .env.local first (highest priority), then .env as fallback
        env_file = [".env.local", ".env"]
        env_file_encoding = 'utf-8'

    @property
    def MYSQL_PASSWD(self) -> str:
        """Return MySQL password from env or file, and cache it in self.MYSQL_PASSWORD"""
        if self.MYSQL_PASSWORD:
            return self.MYSQL_PASSWORD
        elif self.MYSQL_PASSWD_FILE and os.path.isfile(self.MYSQL_PASSWD_FILE):
            with open(self.MYSQL_PASSWD_FILE, "r") as file:
                self.MYSQL_PASSWORD = file.read().strip()
            return self.MYSQL_PASSWORD
        else:
            raise ValueError(
                "MySQL password not found. Set MYSQL_PASSWORD environment variable or MYSQL_PASSWD_FILE."
            )

    @property
    def partner_key(self) -> str:
        if self.SHOPEE_PARTNER_KEY_FILE and os.path.exists(self.SHOPEE_PARTNER_KEY_FILE):
            with open(self.SHOPEE_PARTNER_KEY_FILE) as f:
                self.SHOPEE_PARTNER_KEY = f.read().strip()
        return self.SHOPEE_PARTNER_KEY
    
settings = Settings()
