import logging
from settings import Settings

from backend.__init__ import init as init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    init_db(Settings)


def main() -> None:
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
