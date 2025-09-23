import fastapi
from backend.database import ProjectDB
from backend.models import IncidentUpload
from collections import defaultdict
import datetime

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
async def add_incident(
    request: fastapi.Request, upload: IncidentUpload, file: fastapi.UploadFile
):
    data: ProjectDB = request.app.state.db
    result = data.add_event(upload.station, upload.incident_type)

    if result is None:
        return {"error": "couldn't add the incident to the database"}
    else:
        with open(f"{result}.mp4", "wb") as new_file:
            new_file.write(file.file.read())

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


@router.get("/incident/station/statistics/{station}")
async def get_statistics(request: fastapi.Request, station: str):
    database: ProjectDB = request.app.state.db
    events = database.get_events_by("station", station)
    if events is None or len(events) == 0:
        return {"error": "no incidents found"}

    events_amount = len(events)
    today_events_amount = 0

    amount_by_types: defaultdict[int, int] = defaultdict()
    amount_by_types.default_factory = lambda: 0

    for event in events:
        event_type = event["type"]
        amount_by_types[event_type] += 1

    for event in events:
        timestamp = event["timestamp"]
        today = datetime.datetime.now().date()

        if timestamp.date() == today:
            today_events_amount += 1

    branch = database.get_branch_by_station(station)
    branch = branch[0] if len(branch) > 0 else ""

    return {
        "station": station,
        "branch": branch,
        "events_amount": events_amount,
        "today_events_amount": today_events_amount,
        "amount_by_types": amount_by_types,
        "latest_events": events,
    }
