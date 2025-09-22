import fastapi
from backend.database import ProjectDB

router = fastapi.APIRouter()


@router.get("/info")
async def database_version(request: fastapi.Request) -> dict[str, str]:
    data: ProjectDB = request.app.state.db
    version = data.db.execute_raw("SELECT version()")
    return {
        "db_version": version[0][0] if version is not None else "unknown",
        "server_version": "0.0.1",
    }
