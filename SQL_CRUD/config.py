from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str
    auth0_client_secret: str
    auth0_client_id: str
    auth0_callback_url: str
    secret_key: str
    user_db: str
    password_to_user: str
    host: str
    port: str
    database: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
