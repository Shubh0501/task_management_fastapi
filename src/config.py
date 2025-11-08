from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import Any
import logging
from src.constants import Environment


class Config(BaseSettings):
    DB_URL: str = (
        "postgresql://electrifi:electrifi123@127.0.0.1:5432/atlys_project"
    )
    DB_ASYNC_URL: str = (
        "postgresql+asyncpg://electrifi:electrifi123@127.0.0.1:5432/atlys_project"
    )
    DB_NAME: str = "atlys_project"
    JWT_SECRET_KEY: str = "JWT$ecrETKeYValuePAIR#099100215063"
    JWT_ALGORITHM: str = "HS256"
    AUTH_API_PREFIX: str = "/auth"
    TASK_API_PREFIX: str = "/task"
    APP_ENVIRONMENT_TEMP: str = "LOCAL"
    LOG_LEVEL: str = "info"

    @computed_field
    @property
    def APP_ENVIRONMENT(self) -> Environment:
        if isinstance(self.APP_ENVIRONMENT_TEMP, str):
            return Environment[self.APP_ENVIRONMENT_TEMP.upper()]
        return self.APP_ENVIRONMENT_TEMP

    @computed_field
    @property
    def LOGGING_LEVEL(self) -> int:
        level = (
            getattr(logging, self.LOG_LEVEL.upper())
            if not self.APP_ENVIRONMENT.is_debug
            else logging.DEBUG
        )
        return level


app_configs: dict[str, Any] = {"title": "Atlys Project Management App"}

settings = Config()
