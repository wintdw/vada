from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Required settings (must be set in env or .env)
    API_BASE_URL: str
    INSERT_SERVICE_BASEURL: str
    GOOGLE_APP_SECRET_FILE: str
    GOOGLE_DEVELOPER_TOKEN: str
    CALLBACK_FINAL_URL: str
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_DB: str
    MYSQL_PASSWD_FILE: str


settings = Settings()
