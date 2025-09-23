from pydantic import BaseModel


class IncidentUpload(BaseModel):
    station: str
