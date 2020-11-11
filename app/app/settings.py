from pydantic import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "projectplatform"
    db_user: str = "projectplatform"
    db_pass: str = "projectplatform"

    class config:
        env_prefix = "pp_"


class TestSettings(Settings):
    class Config:
        env_prefix = "pp_test_"
