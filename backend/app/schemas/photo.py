from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PhotoBase(BaseModel):
    filename: str
    storage_url: str
    content_type: str = "image/jpeg"
    file_size: int = Field(..., ge=0)


class PhotoCreate(PhotoBase):
    event_id: int


class PhotoResponse(PhotoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    uploaded_by: int
    is_selected: bool = False
    created_at: datetime


class PhotoSelect(BaseModel):
    photo_ids: list[int] = Field(..., min_length=1, max_length=1000)
    selected: bool = True


class PhotoListResponse(BaseModel):
    items: list[PhotoResponse]
    total: int
    page: int
    page_size: int
