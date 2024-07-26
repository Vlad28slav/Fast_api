"""Add config values from env variables"""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Basic Configuration for FastAPI project"""

    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str
    auth0_client_secret: str
    auth0_client_id: str
    auth0_callback_url: str
    secret_key: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    class Config:
        """Configuration of .env file"""

        env_file: str = ".env"


@lru_cache
def get_settings() -> Settings:
    """Init and return Settings object"""
    return Settings()
