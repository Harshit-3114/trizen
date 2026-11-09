from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.event import Event
from app.models.event_member import event_member
from app.models.user import User


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not bool(current_user.is_active):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if str(current_user.role) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def get_member_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in ("admin", "member"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team membership required",
        )
    return current_user


def is_event_member(db: Session, event_id: int, user_id: int) -> bool:
    stmt = select(event_member.c.user_id).where(
        event_member.c.event_id == event_id,
        event_member.c.user_id == user_id,
    )
    return db.execute(stmt).first() is not None


def ensure_event_access(event_id: int, db: Session, current_user: User) -> Event:
    """Admins of the event + assigned members + global admins may access.

    Everyone else gets 404 (not 403) so event existence is not leaked.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if current_user.role == "admin" and event.admin_id == current_user.id:
        return event
    if current_user.role == "admin":
        # Global admins can manage any event (needed for demo + ops).
        return event
    if is_event_member(db, event_id, current_user.id):
        return event
    raise HTTPException(status_code=404, detail="Event not found")


def ensure_event_admin(event_id: int, db: Session, current_user: User) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.admin_id == current_user.id or current_user.role == "admin":
        return event
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only the event admin can perform this action",
    )
