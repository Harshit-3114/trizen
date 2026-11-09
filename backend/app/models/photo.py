from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)  # object-storage URL or /uploads/... path
    content_type = Column(String, nullable=False, default="image/jpeg")
    file_size = Column(Integer, nullable=False)  # in bytes
    is_selected = Column(Boolean, nullable=False, default=False)  # admin curation flag
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    event = relationship("Event", back_populates="photos")
    uploader = relationship("User")
