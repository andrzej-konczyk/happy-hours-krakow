from pydantic import BaseModel
from uuid import UUID


class Venue(BaseModel):
    id: UUID
    name: str
    address: str
    lat: float
    lng: float
    category: str