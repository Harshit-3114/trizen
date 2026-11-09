from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int
    created_at: datetime


class EventStats(EventResponse):
    total_photos: int = 0
    selected_photos: int = 0
    member_count: int = 0
