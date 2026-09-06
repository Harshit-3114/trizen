# Task 2: Database Models and Migrations

## Objective
Create SQLAlchemy models for Users, Events, Photos, Galleries, and EventMembers, set up database connection, and initialize Alembic for database migrations.

## Files to Create/Modify
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/event.py`
- Create: `backend/app/models/photo.py`
- Create: `backend/app/models/gallery.py`
- Create: `backend/app/models/event_member.py` (association table)
- Create: `backend/app/models/base.py`
- Modify: `alembic/env.py`
- Create: `backend/app/core/database.py` (continued - update with Base import)

## Interfaces
- Consumes: Database connection from database.py
- Produces: SQLAlchemy models for Users, Events, Photos, Galleries, EventMembers

## Steps

### Step 1: Create base model class

Create `backend/app/models/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### Step 2: Create User model

Create `backend/app/models/user.py`:
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin or member
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Step 3: Create Event model

Create `backend/app/models/event.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
```

### Step 4: Create Photo model

Create `backend/app/models/photo.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)  # Reference to Supabase Storage
    file_size = Column(Integer, nullable=False)  # in bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event")
    uploader = relationship("User")
```

### Step 5: Create Gallery model

Create `backend/app/models/gallery.py`:
```python
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
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event")
```

### Step 6: Create EventMember association table

Create `backend/app/models/event_member.py`:
```python
from sqlalchemy import Column, Integer, ForeignKey, Table
from .base import Base

event_member = Table(
    'event_members', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)
```

### Step 7: Update database.py with connection setup

Update `backend/app/core/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
```

### Step 8: Initialize Alembic and create initial migration

```bash
# Alembic is already initialized, but we need to update env.py
# Edit alembic/env.py to import models and set target_metadata
# Then create initial migration
alembic revision --autogenerate -m "initial migration"
```

### Step 9: Run migration to create tables

```bash
alembic upgrade head
```

### Step 10: Commit

```bash
git add backend/app/models/ backend/app/core/database.py alembic/
git commit -m "feat: create database models and migrations"
"
