# Database Models and Migration Design

## Base Model
- File: `backend/app/models/base.py`
- Content: SQLAlchemy DeclarativeBase class named Base.

## User Model
- File: `backend/app/models/user.py`
- Fields:
  - id: Integer, primary key, indexed
  - email: String, unique, indexed, nullable=False
  - password_hash: String, nullable=False
  - role: String, nullable=False (admin or member)
  - is_active: Boolean, default=True
  - created_at: DateTime(timezone=True), server_default=func.now()

## Event Model
- File: `backend/app/models/event.py`
- Fields:
  - id: Integer, primary key, indexed
  - name: String, nullable=False
  - admin_id: Integer, ForeignKey("users.id"), nullable=False
  - created_at: DateTime(timezone=True), server_default=func.now()
- Relationships:
  - admin: relationship("User", foreign_keys=[admin_id])

## Photo Model
- File: `backend/app/models/photo.py`
- Fields:
  - id: Integer, primary key, indexed
  - event_id: Integer, ForeignKey("events.id"), nullable=False
  - uploaded_by: Integer, ForeignKey("users.id"), nullable=False
  - filename: String, nullable=False
  - storage_url: String, nullable=False (Reference to Supabase Storage)
  - file_size: Integer, nullable=False (in bytes)
  - created_at: DateTime(timezone=True), server_default=func.now()
- Relationships:
  - event: relationship("Event")
  - uploader: relationship("User")

## Gallery Model
- File: `backend/app/models/gallery.py`
- Fields:
  - id: Integer, primary key, indexed
  - event_id: Integer, ForeignKey("events.id"), nullable=False
  - slug: String, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4())
  - pin_hash: String, nullable=False (bcrypt hashed PIN)
  - published_at: DateTime(timezone=True) (nullable)
  - created_at: DateTime(timezone=True), server_default=func.now()
- Relationships:
  - event: relationship("Event")

## EventMember Association Table
- File: `backend/app/models/event_member.py`
- Table: event_members
- Columns:
  - event_id: Integer, ForeignKey('events.id'), primary_key=True
  - user_id: Integer, ForeignKey('users.id'), primary_key=True

## Database Connection
- File: `backend/app/core/database.py` (updated)
- Contents:
  - import Base from app.models.base
  - import settings from app.core.config
  - engine = create_engine(settings.DATABASE_URL)
  - SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  - get_db() yields SessionLocal instance
  - create_tables() calls Base.metadata.create_all(bind=engine)

## Alembic Configuration
- File: `alembic/env.py` (updated)
- Changes:
  - Import Base from app.models.base
  - Set target_metadata = Base.metadata

## Assumptions
- Config module (app.core.config) provides a Settings object with DATABASE_URL attribute.
- UUID default uses python's uuid module.
- Relationships are configured as specified.
- No additional fields (e.g., updated_at, username) are required beyond those listed.