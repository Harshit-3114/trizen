from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import secrets
import string

gallery_photos = Table(
    "gallery_photos",
    Base.metadata,
    Column("gallery_id", Integer, ForeignKey("galleries.id", ondelete="CASCADE"), primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True),
)


def _new_slug(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Gallery(Base):
    __tablename__ = "galleries"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False, default="Gallery")
    slug = Column(String, unique=True, index=True, nullable=False, default=lambda: _new_slug())
    pin_hash = Column(String, nullable=False)  # bcrypt hashed PIN
    is_published = Column(Boolean, nullable=False, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    event = relationship("Event", back_populates="galleries")
    photos = relationship("Photo", secondary=gallery_photos)

    def set_pin(self, pin: str):
        """Hash and set the PIN for this gallery."""
        from app.core.security import get_password_hash

        self.pin_hash = get_password_hash(pin)

    def verify_pin(self, pin: str) -> bool:
        """Verify a PIN against the stored hash."""
        from app.core.security import verify_password

        try:
            return verify_password(pin, str(self.pin_hash))
        except Exception:
            return False
