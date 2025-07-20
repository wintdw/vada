from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    TIKTOK_BIZ_API_URL: str
    TIKTOK_BIZ_APP_ID: str
    TIKTOK_BIZ_SECRET: str
    TIKTOK_BIZ_REDIRECT_URI: str

    INSERT_SERVICE_URL: str
    CONNECTOR_CALLBACK_URL: str


settings = Settings()
