import asyncpg
from app.app.settings import Settings
from app.app.backend import config


async def init(settings: Settings):
    config.db = await asyncpg.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_pass,
    )
