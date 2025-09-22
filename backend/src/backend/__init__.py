from backend.database import ProjectDB
from backend.config import Config
from loguru import logger
from backend.app import router
import fastapi
import uvicorn


def main() -> None:
    try:
        config = Config()
        database = ProjectDB(
            config.HOST,
            config.USER,
            config.PASSWORD,
            config.DATABASE_NAME,
            int(config.PORT),
        )

        api = fastapi.FastAPI()
        api.state.db = database
        api.include_router(router)
        uvicorn.run(api)

    except Exception as err:
        logger.error(f"{type(err).__module__ + "." + type(err).__name__}: {err}")
    finally:
        logger.info("exiting...")
