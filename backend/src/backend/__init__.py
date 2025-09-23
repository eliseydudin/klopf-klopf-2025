from backend.database import ProjectDB
from backend.config import Config
from loguru import logger
from backend.app import router
import fastapi
from fastapi.middleware.cors import CORSMiddleware
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
        api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        api.state.db = database
        api.include_router(router)
        uvicorn.run(api)

    except Exception as err:
        logger.error(f"{type(err).__module__ + "." + type(err).__name__}: {err}")
    finally:
        logger.info("exiting...")
