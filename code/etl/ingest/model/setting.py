from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    PORT: str
    APP_ENV: str
    ELASTIC_PASSWD_FILE: str
    ELASTIC_USER: str
    ELASTIC_URL: str
    MAPPINGS_BASEURL: str
    INSERT_BASEURL: str


settings = Settings()
