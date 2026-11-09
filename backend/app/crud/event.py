from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_member import event_member
from app.models.photo import Photo
from app.schemas.event import EventCreate, EventUpdate


def get_event(db: Session, event_id: int) -> Event | None:
    return db.query(Event).filter(Event.id == event_id).first()


def get_events_by_admin(db: Session, admin_id: int) -> list[Event]:
    return db.query(Event).filter(Event.admin_id == admin_id).all()


def get_accessible_events(db: Session, user_id: int, is_global_admin: bool) -> list[Event]:
    if is_global_admin:
        return db.query(Event).order_by(Event.created_at.desc()).all()
    member_event_ids = select(event_member.c.event_id).where(event_member.c.user_id == user_id)
    return (
        db.query(Event)
        .filter((Event.admin_id == user_id) | (Event.id.in_(member_event_ids)))
        .order_by(Event.created_at.desc())
        .all()
    )


def get_event_stats(db: Session, event_id: int) -> dict:
    total = db.query(func.count(Photo.id)).filter(Photo.event_id == event_id).scalar() or 0
    selected = (
        db.query(func.count(Photo.id))
        .filter(Photo.event_id == event_id, Photo.is_selected.is_(True))
        .scalar()
        or 0
    )
    members = (
        db.query(func.count(event_member.c.user_id))
        .filter(event_member.c.event_id == event_id)
        .scalar()
        or 0
    )
    return {"total_photos": total, "selected_photos": selected, "member_count": members}


def create_event(db: Session, event: EventCreate, admin_id: int) -> Event:
    db_event = Event(name=event.name, description=event.description, admin_id=admin_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event(db: Session, event_id: int, event: EventUpdate) -> Event | None:
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    for key, value in event.model_dump(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int) -> Event | None:
    db_event = get_event(db, event_id)
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event
