# Database Models and Migrations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create SQLAlchemy models for Users, Events, Photos, Galleries, and EventMembers, set up database connection, and initialize Alembic for database migrations.

**Architecture:** We will define SQLAlchemy 2.0 declarative models in the backend/app/models directory, configure the database connection in backend/app/core/database.py, and update Alembic environment to use the models' metadata for autogenerate migrations.

**Tech Stack:** Python, SQLAlchemy 2.0, Alembic, PostgreSQL (via settings.DATABASE_URL)

## Global Constraints

- Use SQLAlchemy 2.0 style declarative models.
- Follow the exact field definitions and relationships specified in the task brief.
- Ensure all models import Base from app.models.base.
- The database.py must import Base and settings.
- Alembic env.py must set target_metadata to Base.metadata.
- All code must be compatible with Python 3.8+.

---
### Task 1: Create base model class

**Files:**
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/__init__.py` (if not exists)

**Interfaces:**
- Consumes: None
- Produces: Base class for all models to inherit from

- [ ] **Step 1: Create models directory and __init__.py**

```bash
mkdir -p backend/app/models
touch backend/app/models/__init__.py
```

- [ ] **Step 2: Write the failing test (none needed for structural file)**

Since this is a structural file, we will skip writing a failing test and instead verify the file exists and contains the correct class.

- [ ] **Step 3: Create base.py with Base class**

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

- [ ] **Step 4: Verify file content**

Run: `type backend/app/models/base.py`
Expected: File contains the DeclarativeBase class definition.

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/base.py backend/app/models/__init__.py
git commit -m "feat: create base model class"
```

### Task 2: Create User model

**Files:**
- Create: `backend/app/models/user.py`

**Interfaces:**
- Consumes: Base from .base
- Produces: User model class

- [ ] **Step 1: Write the failing test (none needed for model definition)**

We will verify the model can be imported and has expected columns.

- [ ] **Step 2: Create user.py with User model**

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

- [ ] **Step 3: Verify file content**

Run: `type backend/app/models/user.py`
Expected: File contains the User class with correct columns and relationships.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/user.py
git commit -m "feat: create User model"
```

### Task 3: Create Event model

**Files:**
- Create: `backend/app/models/event.py`

**Interfaces:**
- Consumes: Base from .base
- Produces: Event model class

- [ ] **Step 1: Write the failing test (none needed for model definition)**

- [ ] **Step 2: Create event.py with Event model**

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

- [ ] **Step 3: Verify file content**

Run: `type backend/app/models/event.py`
Expected: File contains the Event class with correct columns and relationship to User.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/event.py
git commit -m "feat: create Event model"
```

### Task 4: Create Photo model

**Files:**
- Create: `backend/app/models/photo.py`

**Interfaces:**
- Consumes: Base from .base
- Produces: Photo model class

- [ ] **Step 1: Write the failing test (none needed for model definition)**

- [ ] **Step 2: Create photo.py with Photo model**

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

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

- [ ] **Step 3: Verify file content**

Run: `type backend/app/models/photo.py`
Expected: File contains the Photo class with correct columns and relationships.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/photo.py
git commit -m "feat: create Photo model"
```

### Task 5: Create Gallery model

**Files:**
- Create: `backend/app/models/gallery.py`

**Interfaces:**
- Consumes: Base from .base
- Produces: Gallery model class

- [ ] **Step 1: Write the failing test (none needed for model definition)**

- [ ] **Step 2: Create gallery.py with Gallery model**

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
    published_at = Column(DateTime(timezone=True))  # nullable
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event")
```

- [ ] **Step 3: Verify file content**

Run: `type backend/app/models/gallery.py`
Expected: File contains the Gallery class with correct columns and relationship.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/gallery.py
git commit -m "feat: create Gallery model"
```

### Task 6: Create EventMember association table

**Files:**
- Create: `backend/app/models/event_member.py`

**Interfaces:**
- Consumes: Base from .base
- Produces: event_members Table object

- [ ] **Step 1: Write the failing test (none needed for table definition)**

- [ ] **Step 2: Create event_member.py with association table**

```python
from sqlalchemy import Column, Integer, ForeignKey, Table
from .base import Base

event_member = Table(
    'event_members', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)
```

- [ ] **Step 3: Verify file content**

Run: `type backend/app/models/event_member.py`
Expected: File contains the event_member Table definition with composite primary key.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/event_member.py
git commit -m "feat: create EventMember association table"
```

### Task 7: Create config.py (if missing)

**Files:**
- Create: `backend/app/core/config.py`

**Interfaces:**
- Consumes: None (reads environment variables)
- Produces: Settings object with DATABASE_URL and other configuration

- [ ] **Step 1: Check if config.py already exists**

If backend/app/core/config.py exists, skip this task.

- [ ] **Step 2: Create config.py with Settings class**

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    # Add other settings as needed (SECRET_KEY, etc.) but only DATABASE_URL is required for now

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 3: Verify file content**

Run: `type backend/app/core/config.py`
Expected: File contains Settings class with DATABASE_URL.

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/config.py
git commit -m "feat: create configuration settings"
```

### Task 8: Update database.py with Base import and session setup

**Files:**
- Modify: `backend/app/core/database.py`

**Interfaces:**
- Consumes: Base from app.models.base, settings from app.core.config
- Produces: engine, SessionLocal, get_db function, create_tables function

- [ ] **Step 1: Backup original database.py (optional)**

- [ ] **Step 2: Rewrite database.py with the following content**

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

- [ ] **Step 3: Verify file content**

Run: `type backend/app/core/database.py`
Expected: File contains the updated imports and functions.

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/database.py
git commit -m "feat: update database connection with Base import"
```

### Task 9: Update Alembic environment to use model metadata

**Files:**
- Modify: `alembic/env.py`

**Interfaces:**
- Consumes: Base from app.models.base
- Produces: target_metadata set for autogenerate support

- [ ] **Step 1: Edit alembic/env.py to import Base and set target_metadata**

Change the line:
```
# target_metadata = mymodel.Base.metadata
```
to:
```
from app.models.base import Base
target_metadata = Base.metadata
```

- [ ] **Step 2: Verify file content**

Run: `type alembic/env.py`
Expected: File contains the import and target_metadata assignment.

- [ ] **Step 3: Commit**

```bash
git add alembic/env.py
git commit -m "feat: update Alembic env.py with model metadata"
```

### Task 10: Create initial migration

**Files:**
- None (creates migration scripts in alembic/versions/)

**Interfaces:**
- Consumes: Updated alembic/env.py and model definitions
- Produces: Migration script for initial schema

- [ ] **Step 1: Generate initial migration using Alembic**

Run: `alembic revision --autogenerate -m "initial migration"`
Expected: Creates a new migration file in alembic/versions/ with the schema creation.

- [ ] **Step 2: Verify migration file**

Check that the migration file contains create table statements for users, events, photos, galleries, event_members.

- [ ] **Step 3: Commit**

```bash
git add alembic/versions/
git commit -m "feat: create initial migration"
```

### Task 11: Run migration to create tables

**Files:**
- None (modifies database)

**Interfaces:**
- Consumes: Migration scripts, database connection
- Produces: Created database tables

- [ ] **Step 1: Run migration to upgrade to head**

Run: `alembic upgrade head`
Expected: Executes the migration against the database, creating tables.

- [ ] **Step 2: Verify tables exist (optional)**

Use a database inspection tool to confirm tables are present.

- [ ] **Step 3: Commit**

```bash
# No code changes, but we can commit the fact that migration was run
# Alternatively, skip commit as this is a database state change.
# We'll create a simple commit to record the migration execution.
git commit --allow-empty -m "feat: run initial migration to create tables"
```

### Task 12: Final verification and commit all

**Files:**
- All created/modified files

**Interfaces:**
- None

- [ ] **Step 1: Run a quick sanity check**

Attempt to import the models and create_tables in a Python script to ensure no import errors.

- [ ] **Step 2: Commit any remaining changes**

```bash
git add .
git commit -m "feat: complete database models and migrations"
```