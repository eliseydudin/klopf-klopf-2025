import fastapi
from backend.database import Database

router = fastapi.APIRouter()


@router.get("/info")
async def database_version(request: fastapi.Request) -> dict[str, str]:
    db: Database = request.app.state.db
    return {
        "db_version": db.execute_raw("SELECT version()")[0][0],
        "server_version": "0.0.1",
    }
