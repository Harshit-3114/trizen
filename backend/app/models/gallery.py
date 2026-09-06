from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class Gallery(Base):
    __tablename__ = "galleries"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    pin_hash = Column(String, nullable=False)  # bcrypt hashed PIN
    published_at = Column(DateTime(timezone=True))  # nullable
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event")