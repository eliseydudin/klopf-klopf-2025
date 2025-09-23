import fastapi
import uuid
import os
from fastapi.responses import StreamingResponse
from backend.database import ProjectDB
from backend.models import IncidentUpload
from collections import defaultdict
import datetime
from .ai.model import predict_incident

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
    temp_id = uuid.uuid1()

    with open(f"videos/{temp_id}.mp4", "wb") as new_file:
        new_file.write(file.file.read())

    event_type_str = predict_incident(f"videos/{temp_id}.mp4")
    event_type = {"fights": 0, "falls": 1}[event_type_str]

    result = data.add_event(upload.station, event_type)

    if result is None:
        return {"error": "couldn't add the incident to the database"}
    else:
        os.rename(f"videos/{temp_id}.mp4", f"videos/{result}.mp4")
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

        event["timestamp"] = event["timestamp"].timestamp()

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


@router.get("/incident/station/stream/{event_id}")
def stream_main(request: fastapi.Request, event_id: int):
    def iterfile():  # (1)
        with open(f"{event_id}.mp4", mode="rb") as file_like:  # (2)
            yield from file_like  # (3)

    return StreamingResponse(iterfile(), media_type="video/mp4")
