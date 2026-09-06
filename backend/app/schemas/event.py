from pydantic import BaseModel, Field
from typing import Optional

class EventBase(BaseModel):
    name: str

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    admin_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True