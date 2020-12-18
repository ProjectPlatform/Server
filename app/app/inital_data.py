import logging
import asyncio
import os

import firebase_admin

from app.app.settings import Settings
from app.app.backend import init as init_db
from configparser import ConfigParser

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


async def init() -> None:
    settings = Settings(db_host=config['db']['PP_DB_HOST'],
                        db_port=5432,
                        db_name=config['db']['PP_DB_NAME'],
                        db_user=config['db']['PP_DB_USER'],
                        db_pass=config['db']['PP_DB_PASS'])
    log.info("init db")
    await init_db(settings=settings)


async def main() -> None:
    default_app = firebase_admin.initialize_app()
    # log.info(os.path.dirname(__file__))
    log.info("Creating initial data")
    await init()
    log.info("Initial data created")


loop = asyncio.get_event_loop()
loop.create_task(main())

# try:
#     loop = asyncio.get_event_loop()
# except RuntimeError:
#     loop = None
#
# if loop and loop.is_running():
#     print('Async event loop already running')
#     tsk = loop.create_task(main())
#     # tsk.add_done_callback(                                          # optional
#     #     lambda t: print(f'Task done: '                              # optional
#     #                     f'{t.result()=} << return val of main()'))  # optional (using py38)
# else:
#     print('Starting new event loop')
#     asyncio.run(main())