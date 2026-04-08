from pydantic import BaseModel
from uuid import UUID
from datetime import time


class Deal(BaseModel):
    id:          UUID
    venue_id:    UUID
    description: str
    start_time:  time
    end_time:    time
    days_of_week: list[str]
    type:         str        = "mixed"
    tags:         list[str]  = []
    value_score:  int        = 1