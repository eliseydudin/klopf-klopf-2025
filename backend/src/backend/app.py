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


@router.get("/incident/station/{station}")
async def get_incidents(
    request: fastapi.Request, station: str, limit: int | None = None
):
    database: ProjectDB = request.app.state.db
    events = database.get_events_by("station", station, limit)

    if events is None or len(events) == 0:
        return {"error": "no incidents found"}

    return {"events": events}


@router.get("/incident/station/branch/{station}")
async def get_branch(request: fastapi.Request, station: str):
    database: ProjectDB = request.app.state.db
    branches = database.get_branch_by_station(station=station)

    if branches is None or len(branches) == 0:
        return {"error": "no branches found"}

    return {"branches": branches}
