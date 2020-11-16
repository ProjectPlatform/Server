import logging
import asyncio
from app.app.settings import Settings
import os
from app.app.backend import init as init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    settings = Settings(db_host=os.environ["PP_DB_HOST"],
                        db_port=5432,
                        db_name=os.environ["PP_DB_NAME"],
                        db_user=os.environ["PP_DB_USER"],
                        db_pass=os.environ["PP_DB_PASS"])
    logger.info("init db")
    await init_db(settings=settings)


async def main() -> None:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


loop = asyncio.get_event_loop()
loop.create_task(main())
