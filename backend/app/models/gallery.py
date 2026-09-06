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
    
    def set_pin(self, pin: str):
        """Hash and set the PIN for this gallery."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.pin_hash = pwd_context.hash(pin)

    def verify_pin(self, pin: str) -> bool:
        """Verify a PIN against the stored hash."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(pin, self.pin_hash)