from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import ensure_event_access, ensure_event_admin
from app.core.security import get_current_user
from app.crud import event as event_crud
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse, EventStats, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventStats])
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Events visible to the caller: owned + assigned (+ all for global admins)."""
    events = event_crud.get_accessible_events(
        db, int(current_user.id), str(current_user.role) == "admin"
    )
    result: list[EventStats] = []
    for ev in events:
        stats = event_crud.get_event_stats(db, int(ev.id))
        result.append(
            EventStats(
                id=int(ev.id),
                name=str(ev.name),
                description=str(ev.description or ""),
                admin_id=int(ev.admin_id),
                created_at=ev.created_at,  # type: ignore[arg-type]
                **stats,
            )
        )
    return result


@router.post("", response_model=EventResponse, status_code=201)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if str(current_user.role) not in ("admin", "member"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return event_crud.create_event(db, payload, admin_id=int(current_user.id))


@router.get("/{event_id}", response_model=EventStats)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = ensure_event_access(event_id, db, current_user)
    stats = event_crud.get_event_stats(db, int(event.id))
    return EventStats(
        id=int(event.id),
        name=str(event.name),
        description=str(event.description or ""),
        admin_id=int(event.admin_id),
        created_at=event.created_at,  # type: ignore[arg-type]
        **stats,
    )


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_event_admin(event_id, db, current_user)
    updated = event_crud.update_event(db, event_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_event_admin(event_id, db, current_user)
    event_crud.delete_event(db, event_id)
    return None
