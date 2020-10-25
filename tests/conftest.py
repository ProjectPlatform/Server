import pytest
import backend
from settings import TestSettings


@pytest.fixture
async def db():
    await backend.init(TestSettings())
    yield backend.config.db
    await backend.config.db.close()
