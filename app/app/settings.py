import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    db_host: str = os.environ.get('DB_HOST')
    db_port: int = 5432
    db_name: str = os.environ.get('DB_NAME')
    db_user: str = os.environ.get('DB_USER')
    db_pass: str = os.environ.get('DB_HOST')

    class Config:
        env_prefix = "PP_"


class TestSettings(Settings):
    class Config:
        env_prefix = "PP_TEST_"
