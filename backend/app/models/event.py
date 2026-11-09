from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False, default="")
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
    photos = relationship("Photo", back_populates="event", cascade="all, delete-orphan")
    galleries = relationship("Gallery", back_populates="event", cascade="all, delete-orphan")
