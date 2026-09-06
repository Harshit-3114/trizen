from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GalleryBase(BaseModel):
    event_id: int
    
class GalleryCreate(GalleryBase):
    pin: str
    
class GalleryResponse(GalleryBase):
    id: int
    slug: str
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        orm_mode = True

class GalleryPinVerify(BaseModel):
    pin: str