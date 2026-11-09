from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.photo import PhotoResponse


class GalleryCreate(BaseModel):
    title: str = Field(default="Gallery", min_length=1, max_length=200)
    pin: str = Field(..., min_length=4, max_length=12, pattern="^[0-9]{4,12}$")
    photo_ids: list[int] = Field(default_factory=list, max_length=2000)


class GalleryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    pin: str | None = Field(default=None, min_length=4, max_length=12, pattern="^[0-9]{4,12}$")
    photo_ids: list[int] | None = Field(default=None, max_length=2000)
    is_published: bool | None = None


class GalleryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    title: str
    slug: str
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    photo_count: int = 0


class GalleryDetailResponse(GalleryResponse):
    photos: list[PhotoResponse] = []


class GalleryPinVerify(BaseModel):
    pin: str = Field(..., min_length=4, max_length=12)


class PublicGalleryResponse(BaseModel):
    title: str
    slug: str
    event_name: str
    photos: list[PhotoResponse]
