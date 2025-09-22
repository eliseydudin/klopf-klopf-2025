from backend.database import Database
from backend.config import HOST, USER, PASSWORD, DATABASE_NAME, PORT
from loguru import logger
from backend.app import router
import fastapi
import uvicorn


def main() -> None:
    try:
        database = Database(HOST, USER, PASSWORD, DATABASE_NAME, PORT)

        api = fastapi.FastAPI()
        api.state.db = database
        api.include_router(router)

        uvicorn.run(api)

    except Exception as err:
        logger.error(f"{err}")
    finally:
        logger.info("exiting...")
