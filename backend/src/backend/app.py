import fastapi
from backend.database import ProjectDB
from backend.models import IncidentUpload

router = fastapi.APIRouter()


@router.get("/info")
async def database_version(request: fastapi.Request) -> dict[str, str]:
    data: ProjectDB = request.app.state.db
    version = data.db.execute_raw("SELECT version()")
    return {
        "db_version": version[0][0] if version is not None else "unknown",
        "server_version": "0.0.1",
    }


@router.post("/incident/add")
async def add_incident(request: fastapi.Request, upload: IncidentUpload):
    data: ProjectDB = request.app.state.db
    result = data.add_event(upload.station, upload.incident_type)

    if result is None:
        return {"error": "couldn't add the incident to the database"}
    else:
        return {"id": str(result)}
