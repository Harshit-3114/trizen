from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event import EventCreate

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