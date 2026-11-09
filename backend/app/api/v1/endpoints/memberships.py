from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import ensure_event_admin, is_event_member
from app.core.security import get_current_user
from app.crud.user import get_user_by_email
from app.models.event import Event
from app.models.event_member import event_member
from app.models.user import User
from app.schemas.member import MemberAdd, MemberResponse

router = APIRouter(prefix="/events/{event_id}/members", tags=["members"])


def _member_payload(db: Session, event: Event) -> list[MemberResponse]:
    stmt = select(event_member.c.user_id).where(event_member.c.event_id == int(event.id))
    member_ids = [row[0] for row in db.execute(stmt).fetchall()]
    ids = list({*member_ids, int(event.admin_id)})
    users = db.query(User).filter(User.id.in_(ids)).all() if ids else []
    return [
        MemberResponse(
            id=int(u.id),
            email=str(u.email),
            full_name=str(u.full_name or ""),
            role="admin" if int(u.id) == int(event.admin_id) else "member",
        )
        for u in users
    ]


@router.get("", response_model=list[MemberResponse])
def list_members(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    allowed = (
        int(event.admin_id) == int(current_user.id)
        or str(current_user.role) == "admin"
        or is_event_member(db, event_id, int(current_user.id))
    )
    if not allowed:
        raise HTTPException(status_code=404, detail="Event not found")
    return _member_payload(db, event)


@router.post("", response_model=MemberResponse, status_code=201)
def add_member(
    event_id: int,
    payload: MemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin adds a team member by email (the SRD workflow)."""
    event = ensure_event_admin(event_id, db, current_user)
    user = get_user_by_email(db, str(payload.email))
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="No registered user with that email. Ask them to register first.",
        )
    if int(user.id) == int(event.admin_id):
        raise HTTPException(status_code=400, detail="User is already the event admin")
    if is_event_member(db, event_id, int(user.id)):
        raise HTTPException(status_code=400, detail="User is already a member of this event")
    db.execute(event_member.insert().values(event_id=event_id, user_id=int(user.id)))
    db.commit()
    return MemberResponse(
        id=int(user.id), email=str(user.email),
        full_name=str(user.full_name or ""), role="member",
    )


@router.delete("/{user_id}", status_code=204)
def remove_member(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = ensure_event_admin(event_id, db, current_user)
    if user_id == int(event.admin_id):
        raise HTTPException(status_code=400, detail="Cannot remove the event admin")
    if not is_event_member(db, event_id, user_id):
        raise HTTPException(status_code=404, detail="Membership not found")
    db.execute(
        event_member.delete().where(
            event_member.c.event_id == event_id,
            event_member.c.user_id == user_id,
        )
    )
    db.commit()
    return None


# Back-compat: some clients POST /{user_id}. Keep it working.
@router.post("/{user_id}", response_model=MemberResponse, status_code=201)
def add_member_by_id(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.crud.user import get_user

    event = ensure_event_admin(event_id, db, current_user)
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if int(user.id) == int(event.admin_id) or is_event_member(db, event_id, int(user.id)):
        raise HTTPException(status_code=400, detail="User is already part of this event")
    db.execute(event_member.insert().values(event_id=event_id, user_id=int(user.id)))
    db.commit()
    return MemberResponse(
        id=int(user.id), email=str(user.email),
        full_name=str(user.full_name or ""), role="member",
    )
