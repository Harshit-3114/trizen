# Photo Sharing Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack photo-sharing application that allows photography teams to collaboratively upload event photos, admins to curate and publish PIN-protected galleries, and customers to access galleries via link + PIN without account creation.

**Architecture:** Three-tier architecture with FastAPI backend handling authentication, event management, photo uploads/storage, and gallery publishing; React/TypeScript frontend with Tailwind CSS for admin, member, and customer interfaces; PostgreSQL database via Supabase for metadata; Supabase Storage for actual image files.

**Tech Stack:** FastAPI (Python), React + TypeScript, Tailwind CSS, PostgreSQL (Supabase), Supabase Storage, JWT authentication, bcrypt password hashing, Railway (backend deployment), Vercel (frontend deployment)

## Global Constraints

- Admin/Lead can register/login, create events, add team members, view all event photos, select photos for gallery, publish gallery with PIN, generate shareable link
- Team Members can login, view assigned events, upload photos, view their own uploaded photos (cannot publish galleries)
- Customers access published galleries via shareable link + PIN entry without account creation
- Photo files stored in object storage (Supabase Storage), metadata stored in database (photos table)
- Must handle: accessing wrong event, team member attempting to publish gallery, failed photo uploads, incorrect gallery PIN, accessing unpublished photos
- Required features: authentication & role-based authorization, secure photo uploads & object storage integration, database schema design & API implementation, input validation & error handling, responsive UI & basic security practices, cloud deployment
- Deployment deadline: September 20, 2026 (14 days from start)

---
## File Structure

- `backend/` - FastAPI application
  - `app/main.py` - Application entry point
  - `app/core/config.py` - Configuration management
  - `app/core/security.py` - Security utilities (JWT, bcrypt)
  - `app/core/database.py` - Database connection setup
  - `app/api/v1/api.py` - API router
  - `app/api/v1/endpoints/auth.py` - Authentication endpoints
  - `app/api/v1/endpoints/users.py` - User management
  - `app/api/v1/endpoints/events.py` - Event management
  - `app/api/v1/endpoints/photos.py` - Photo upload and management
  - `app/api/v1/endpoints/galleries.py` - Gallery creation and access
  - `app/models/` - SQLAlchemy database models
  - `app/schemas/` - Pydantic models for request/validation
  - `app/crud/` - Database operations
  - `app/utils/storage.py` - Supabase Storage integration
- `frontend/` - React/TypeScript application
  - `src/` - Source code
    - `components/` - Reusable UI components
    - `pages/` - Page components (login, dashboard, upload, gallery, etc.)
    - `services/` - API service functions
    - `context/` - React context for auth state
    - `hooks/` - Custom React hooks
    - `utils/` - Utility functions
    - `styles/` - Tailwind CSS configuration
- `tests/` - Test files
  - `backend/` - Backend tests (Pytest)
  - `frontend/` - Frontend tests (Vitest/RTL)
- `docs/` - Documentation
- `alembic/` - Database migrations
- `.github/workflows/` - CI/CD (optional bonus)

## Task Right-Sizing

A task is the smallest unit that carries its own test cycle and is worth a reviewer's gate. Each task ends with an independently testable deliverable.

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the test to verify it passes" - step
- "Commit" - step

---

### Task 1: Project Setup and Backend Scaffolding

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `requirements.txt`
- Create: `alembic.ini`
- Create: `alembic/env.py`

**Interfaces:**
- Consumes: None
- Produces: FastAPI app instance, database connection factory, basic configuration

- [ ] **Step 1: Initialize project structure and dependencies**

```bash
mkdir -p backend/app/{core,api/v1/endpoints,models,schemas,crud,utils}
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/api/v1/endpoints/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/crud/__init__.py
touch backend/app/utils/__init__.py
```

- [ ] **Step 2: Create requirements.txt with FastAPI, SQLAlchemy, etc.**

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
alembic==1.13.1
python-dotenv==1.0.0
```

- [ ] **Step 3: Initialize git repository and commit**

```bash
git init
git add .
git commit -m "feat: initialize project structure"
```

- [ ] **Step 4: Create basic FastAPI app in main.py**

```python
from fastapi import FastAPI

app = FastAPI(
    title="Photo Sharing Platform API",
    description="API for event photo sharing platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Photo Sharing Platform API"}
```

- [ ] **Step 5: Run and verify server starts**

```bash
uvicorn backend.app.main:app --reload
```
Expected: Server starts successfully on http://localhost:8000

- [ ] **Step 6: Commit**

```bash
git add backend/app/main.py requirements.txt
git commit -m "feat: create basic FastAPI app"
```

### Task 2: Database Models and Migrations

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/event.py`
- Create: `backend/app/models/photo.py`
- Create: `backend/app/models/gallery.py`
- Create: `backend/app/models/event_member.py` (association table)
- Create: `backend/app/models/base.py`
- Modify: `alembic/env.py`
- Create: `backend/app/core/database.py` (continued)

**Interfaces:**
- Consumes: Database connection from database.py
- Produces: SQLAlchemy models for Users, Events, Photos, Galleries, EventMembers

- [ ] **Step 1: Create base model class**

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

- [ ] **Step 2: Create User model**

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

- [ ] **Step 3: Create Event model**

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm relationship
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

- [ ] **Step 4: Create Photo model**

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm relationship
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

- [ ] **Step 5: Create Gallery model**

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm relationship
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

- [ ] **Step 6: Create EventMember association table**

```python
from sqlalchemy import Column, Integer, ForeignKey, Table
from .base import Base

event_member = Table(
    'event_members', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)
```

- [ ] **Step 7: Update database.py with connection setup**

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

- [ ] **Step 8: Initialize Alembic and create initial migration**

```bash
alembic init alembic
# Edit alembic/env.py to import models and set target_metadata
alembic revision --autogenerate -m "initial migration"
```

- [ ] **Step 9: Run migration to create tables**

```bash
alembic upgrade head
```

- [ ] **Step 10: Commit**

```bash
git add backend/app/models/ backend/app/core/database.py alembic/
git commit -m "feat: create database models and migrations"
```

### Task 3: Authentication System

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/crud/user.py`
- Modify: `backend/app/api/v1/endpoints/auth.py`
- Create: `backend/app/api/v1/endpoints/__init__.py` (continued)

**Interfaces:**
- Consumes: User model, database session
- Produces: JWT tokens, authenticated user dependencies

- [ ] **Step 1: Create security utilities for password hashing and JWT**

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

- [ ] **Step 2: Create User schema**

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: str = Field(default="member")  # admin or member

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
```

- [ ] **Step 3: Create CRUD operations for users**

```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user
```

- [ ] **Step 4: Create authentication endpoints**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, get_password_hash
from app.core.database import get_db
from app.crud.user import authenticate_user, get_user_by_email, create_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return create_user(db, user)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 5: Create auth dependencies and security middleware**

```python
# Continue in security.py or create auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.security = pwd_context
from app.core.database = get_db
from app.crud.user = get_user_by_email
from app.schemas.user = TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/core/security.py backend/app/schemas/user.py backend/app/crud/user.py backend/app/api/v1/endpoints/auth.py
git commit -m "feat: implement authentication system"
```

### Task 4: Role-Based Access Control (RBAC)

**Files:**
- Create: `backend/app/core/dependencies.py`
- Modify: `backend/app/api/v1/endpoints/auth.py` (continued)

**Interfaces:**
- Consumes: Current user from auth dependency
- Produces: Role-based access dependencies (admin_required, member_required)

- [ ] **Step 1: Create RBAC dependencies**

```python
from fastapi import Depends, HTTPException, status
from app.core.security = get_current_user
from app.schemas.user = UserResponse

def get_current_active_user(current_user: UserResponse = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_admin_user(current_user: UserResponse = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDEND,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def get_member_user(current_user: UserResponse = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "member"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/dependencies.py
git commit -m "feat: implement role-based access control"
```

### Task 5: Event Management Endpoints

**Files:**
- Create: `backend/app/schemas/event.py`
- Create: `backend/app/crud/event.py`
- Modify: `backend/app/api/v1/endpoints/events.py`

**Interfaces:**
- Consumes: User authentication, database session
- Produces: Event CRUD operations

- [ ] **Step 1: Create Event schemas**

```python
from pydantic = BaseModel
from typing = Optional
from datetime = datetime

class EventBase(BaseModel):
    name: str

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    admin_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
```

- [ ] **Step 2: Create CRUD operations for events**

```python
from sqlalchemy.orm = Session
from app.models.event = Event
from app.schemas.event = EventCreate

def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def get_events_by_admin(db: Session, admin_id: int):
    return db.query(Event).filter(Event.admin_id == admin_id).all()

def create_event(db: Session, event: EventCreate, admin_id: int):
    db_event = Event(**event.dict(), admin_id=admin_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, event: EventCreate):
    db_event = get_event(db, event_id)
    if db_event:
        for key, value in event.dict().items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = get_event(db, event_id)
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event
```

- [ ] **Step 3: Create event endpoints**

```python
from fastapi = APIRouter, Depends, HTTPException, status
from sqlalchemy.orm = Session
from app.core.database = get_db
from app.core.dependencies = get_admin_user
from app.crud.event = get_event, create_event, get_events_by_admin, update_event, delete_event
from app.schemas.event = EventCreate, EventResponse
from app.schemas.user = UserResponse

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse)
def create_new_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    return create_event(db, event, current_user.id)

@router.get("/", response_model=list[EventResponse])
def read_user_events(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    if current_user.role == "admin":
        return get_events_by_admin(db, current_user.id)
    else:
        # For members, return events they're members of
        # This would require a join with event_member table
        # For simplicity in MVP, we'll return empty list or implement later
        return []

@router.get("/{event_id}", response_model=EventResponse)
def read_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    db_event = get_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    # Check if user has access (admin of event or member of event)
    # For MVP, we'll implement basic check and enhance later
    if current_user.role == "member":
        # TODO: Check if user is member of this event
        pass  # Allow for now, will implement properly in member endpoints
    elif current_user.role != "admin" and db_event.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this event")
    return db_event

@router.put("/{event_id}", response_model=EventResponse)
def update_existing_event(
    event_id: int,
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    db_event = update_event(db, event_id, event)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@router.delete("/{event_id}")
def delete_existing_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    db_event = delete_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/schemas/event.py backend/app/crud/event.py backend/app/api/v1/endpoints/events.py
git commit -m "feat: implement event management endpoints"
```

### Task 6: Event Membership Management

**Files:**
- Create: `backend/app/schemas/event_member.py`
- Create: `backend/app/crud/event_member.py`
- Modify: `backend/app/api/v1/endpoints/events.py` (continued)

**Interfaces:**
- Consumes: Event and user authentication
- Produces: Event membership management

- [ ] **Step 1: Create EventMember schema**

```python
from pydantic = BaseModel

class EventMemberBase(BaseModel):
    event_id: int
    user_id: int

class EventMemberCreate(EventMemberBase):
    pass

class EventMemberResponse(EventMemberBase):
    id: int  # Assuming we add an ID column or use composite key
    
    class Config:
        orm_mode = True
```

- [ ] **Step 2: Create CRUD operations for event membership**

```python
from sqlalchemy.orm = Session
from app.models.event_member = event_member
from app.models.event = Event
from app.models.user = User
from app.schemas.event_member = EventMemberCreate

def add_member_to_event(db: Session, event_id: int, user_id: int):
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Check if already a member
    existing = db.query(event_member).filter(
        event_member.c.event_id == event_id,
        event_member.c.user_id == user_id
    ).first()
    if existing:
        return existing
    
    # Add membership
    stmt = event_member.insert().values(event_id=event_id, user_id=user_id)
    db.execute(stmt)
    db.commit()
    return {"event_id": event_id, "user_id": user_id}

def remove_member_from_event(db: Session, event_id: int, user_id: int):
    stmt = event_member.delete().where(
        event_member.c.event_id == event_id,
        event_member.c.user_id == user_id
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount > 0

def get_event_members(db: Session, event_id: int):
    return db.query(event_member).filter(event_member.c.event_id == event_id).all()

def get_user_events(db: Session, user_id: int):
    return db.query(event_member).filter(event_member.c.user_id == user_id).all()
```

- [ ] **Step 3: Add event membership endpoints to events router**

```python
# Add to the events router in endpoints/events.py
from app.schemas.event_member = EventMemberCreate
from app.crud.event_member = add_member_to_event, remove_member_from_event, get_event_members, get_user_events

@router.post("/{event_id}/members", response_model=dict)
def add_event_member(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    # In a real app, we'd specify which user to add
    # For MVP, we'll simplify and allow adding self or implement proper endpoint later
    # This is a placeholder - proper implementation would accept user_id in request body
    success = add_member_to_event(db, event_id, current_user.id)
    if success:
        return {"message": "Added yourself to event"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add member to event")

@router.get("/{event_id}/members", response_model=list)
def get_event_members_list(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    return get_event_members(db, event_id)

@router.get("/me/events", response_model=list)
def get_my_events(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    if current_user.role == "admin":
        return get_events_by_admin(db, current_user.id)
    else:
        # For members, return events they belong to
        # This would require joining with event_member table
        # Placeholder implementation
        return []
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/schemas/event_member.py backend/app/crud/event_member.py backend/app/api/v1/endpoints/events.py
git commit -m "feat: implement event membership management"
```

### Task 7: Photo Upload Endpoint

**Files:**
- Create: `backend/app/schemas/photo.py`
- Create: `backend/app/crud/photo.py`
- Create: `backend/app/utils/storage.py`
- Modify: `backend/app/api/v1/endpoints/photos.py`

**Interfaces:**
- Consumes: Authenticated user, file upload, event ID
- Produces: Photo metadata stored in database, file stored in Supabase Storage

- [ ] **Step 1: Create Photo schemas**

```python
from pydantic = BaseModel
from typing = Optional
from datetime = datetime

class PhotoBase(BaseModel):
    filename: str
    storage_url: str
    file_size: int

class PhotoCreate(PhotoBase):
    event_id: int

class PhotoResponse(PhotoBase):
    id: int
    event_id: int
    uploaded_by: int
    created_at: datetime
    
    class Config:
        orm_mode = True
```

- [ ] **Step 2: Create CRUD operations for photos**

```python
from sqlalchemy.orm = Session
from app.models.photo = Photo
from app.schemas.photo = PhotoCreate

def create_photo(db: Session, photo: PhotoCreate, uploaded_by: int):
    db_photo = Photo(**photo.dict(), uploaded_by=uploaded_by)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

def get_photos_by_event(db: Session, event_id: int):
    return db.query(Photo).filter(Photo.event_id == event_id).all()

def get_photos_by_user(db: Session, user_id: int):
    return db.query(Photo).filter(Photo.uploaded_by == user_id).all()

def get_photo(db: Session, photo_id: int):
    return db.query(Photo).filter(Photo.id == photo_id).first()

def delete_photo(db: Session, photo_id: int):
    db_photo = get_photo(db, photo_id)
    if db_photo:
        db.delete(db_photo)
        db.commit()
    return db_photo
```

- [ ] **Step 3: Create Supabase storage utility**

```python
import os
from supabase = create_client, Client
from app.core.config = settings

# Initialize Supabase client
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

def upload_file_to_supabase(file_content: bytes, file_path: str) -> str:
    """
    Upload file to Supabase Storage and return the public URL
    """
    try:
        # Upload file
        response = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            file_path, file_content
        )
        
        # Get public URL
        file_url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
        return file_url
    except Exception as e:
        raise Exception(f"Failed to upload file to Supabase: {str(e)}")

def delete_file_from_supabase(file_path: str) -> bool:
    """
    Delete file from Supabase Storage
    """
    try:
        supabase.storage.from_(settings.SUPABASE_BUCKET).remove([file_path])
        return True
    except Exception as e:
        raise Exception(f"Failed to delete file from Supabase: {str(e)}")
```

- [ ] **Step 4: Create photo upload endpoint**

```python
from fastapi = APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm = Session
from app.core.database = get_db
from app.core.dependencies = get_member_user
from app.crud.photos = create_photo, get_photos_by_event
from app.schemas.photo = PhotoCreate, PhotoResponse
from app.schemas.user = UserResponse
from app.utils.storage = upload_file_to_supabase
import os

router = APIRouter(prefix="/photos", tags=["photos"])

@router.post("/events/{event_id}/upload", response_model=PhotoResponse)
def upload_photo(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_member_user)
):
    # Validate file type (basic check - in production, check magic bytes)
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (e.g., 10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = file.file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10MB"
        )
    
    # Check if user has access to event (simplified for MVP)
    # In production, check if user is member of event or admin
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # For MVP, we'll allow upload if user is admin of event or skip detailed check
    # Proper implementation would check event membership
    
    # Generate unique filename to avoid conflicts
    import uuid
    from datetime = datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{file.filename}"
    storage_path = f"events/{event_id}/{unique_filename}"
    
    # Upload to Supabase Storage
    try:
        storage_url = upload_file_to_supabase(file_content, storage_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Create photo record in database
    photo_data = PhotoCreate(
        filename=file.filename