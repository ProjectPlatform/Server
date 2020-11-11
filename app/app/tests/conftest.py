import asyncio
import pytest
from app.app import backend
from app.app.settings import TestSettings
import pathlib


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db():
    await backend.init(TestSettings())
    await backend.config.db.execute(
        """
        CREATE SCHEMA IF NOT EXISTS tests;
        SET search_path TO tests;"""
    )
    p = pathlib.Path.cwd()
    while not (p / "db").exists():
        p = p.parent
    schema_script = (p / "db" / "schema.sql").read_text()
    await backend.config.db.execute(schema_script)
    yield backend.config.db

    await backend.config.db.execute(
        """
        SET search_path TO public;
        DROP SCHEMA tests CASCADE;"""
    )
    await backend.config.db.close()
