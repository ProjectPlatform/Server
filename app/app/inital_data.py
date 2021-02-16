import logging
import asyncio
import os

import firebase_admin
from firebase_admin import credentials

from app.app.settings import Settings
from app.app.backend import init as init_db
from configparser import ConfigParser
from dotenv import load_dotenv

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def init() -> None:
    settings = Settings(db_host=os.environ.get("PP_DB_HOST"),
                        db_port=5432,
                        db_name=os.environ.get("PP_DB_NAME"),
                        db_user=os.environ.get("PP_DB_USER"),
                        db_pass=os.environ.get("PP_DB_PASS"))
    log.info("init db")
    await init_db(settings=settings)


async def main() -> None:
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    cred = credentials.Certificate(
        (os.path.join(os.path.dirname(__file__), 'server-7f82a-firebase-adminsdk-leob0-215c5fb60a.json')))
    firebase_admin.initialize_app(cred)
    log.info("Creating initial data")
    await init()
    log.info("Initial data created")
    #await websockets.bug()


loop = asyncio.get_event_loop()
loop.create_task(main())
