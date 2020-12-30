import logging
import asyncio
import os

import firebase_admin
from firebase_admin import credentials

from app.app.backend import init as init_db
from configparser import ConfigParser

from app.app.settings import Settings

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

from app.app.src import websockets

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def init() -> None:
    settings = Settings(db_host=config['db']['PP_DB_HOST'],
                        db_port=5432,
                        db_name=config['db']['PP_DB_NAME'],
                        db_user=config['db']['PP_DB_USER'],
                        db_pass=config['db']['PP_DB_PASS'])
    log.info("init db")
    await init_db(settings=settings)


async def main() -> None:
    cred = credentials.Certificate(
        (os.path.join(os.path.dirname(__file__), 'server-7f82a-firebase-adminsdk-leob0-215c5fb60a.json')))
    # cred = credentials.Certificate((os.path.join(os.path.dirname(__file__), 'server-7f82a-firebase-adminsdk-leob0-215c5fb60a.json'))"./server-7f82a-firebase-adminsdk-leob0-215c5fb60a.json")
    firebase_admin.initialize_app(cred)
    log.info("Creating initial data")
    await init()
    log.info("Initial data created")
    #await websockets.bug()


loop = asyncio.get_event_loop()
loop.create_task(main())
