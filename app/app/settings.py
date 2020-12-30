import os
from configparser import ConfigParser

from pydantic import BaseSettings

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


class Settings(BaseSettings):
    db_host: str = config['db']['PP_DB_HOST']
    db_port: int = 5432
    db_name: str = config['db']['PP_DB_NAME']
    db_user: str = config['db']['PP_DB_USER']
    db_pass: str = config['db']['PP_DB_PASS']

    class сonfig:
        env_prefix = "pp_"


class TestSettings(Settings):
    class Config:
        env_prefix = "pp_test_"
