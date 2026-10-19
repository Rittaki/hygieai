from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: Literal["local", "test", "production"] = "local"
    app_name: str = "HygieAI API"


@lru_cache
def get_settings() -> Settings:
    return Settings()
