from backend.database import Database
from backend.config import HOST, USER, PASSWORD, DATABASE_NAME, PORT
from loguru import logger


def main() -> None:
    try:
        database = Database(HOST, USER, PASSWORD, DATABASE_NAME, PORT)
        logger.info(f"{database.execute_raw("SELECT version()")[0][0]}")
    except Exception as err:
        logger.error(f"{err}")
    finally:
        logger.info("exiting...")
