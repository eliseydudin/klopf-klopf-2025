from pydantic import BaseModel


class IncidentUpload(BaseModel):
    station: str
    incident_type: int
