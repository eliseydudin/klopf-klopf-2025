import fastapi
from backend.database import ProjectDB

router = fastapi.APIRouter()


@router.get("/info")
async def database_version(request: fastapi.Request) -> dict[str, str]:
    data: ProjectDB = request.app.state.db
    return {
        "db_version": data.db.execute_raw("SELECT version()")[0][0],
        "server_version": "0.0.1",
    }
