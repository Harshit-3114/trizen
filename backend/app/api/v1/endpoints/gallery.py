"""Gallery endpoints.

Team flow (authenticated, /api/v1/events/{id}/galleries...):
  admin creates gallery with PIN + photo selection, publishes, shares link.

Customer flow (public, no account, /api/v1/public/galleries/{slug}...):
  open link -> enter PIN -> view published photos only.
"""

import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import ensure_event_admin
from app.core.security import get_current_user
from app.crud import gallery as gallery_crud
from app.models.event import Event
from app.models.user import User
from app.schemas.gallery import (
    GalleryCreate,
    GalleryDetailResponse,
    GalleryPinVerify,
    GalleryResponse,
    GalleryUpdate,
    PublicGalleryResponse,
)
from app.schemas.photo import PhotoResponse

team_router = APIRouter(prefix="/events/{event_id}/galleries", tags=["galleries"])

# --- brute-force guard for public PIN checks (in-memory, per-process) ---
_pin_attempts: dict[str, list[float]] = defaultdict(list)
_PIN_WINDOW_S = 10 * 60
_PIN_MAX_ATTEMPTS = 20


def _check_pin_rate_limit(slug: str) -> None:
    now = time.time()
    attempts = [t for t in _pin_attempts[slug] if now - t < _PIN_WINDOW_S]
    _pin_attempts[slug] = attempts
    if len(attempts) >= _PIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many PIN attempts. Please try again later.",
        )


def _record_pin_attempt(slug: str, success: bool) -> None:
    if success:
        _pin_attempts.pop(slug, None)
    else:
        _pin_attempts[slug].append(time.time())


def _to_response(gallery) -> GalleryResponse:
    return GalleryResponse(
        id=int(gallery.id),
        event_id=int(gallery.event_id),
        title=str(gallery.title),
        slug=str(gallery.slug),
        is_published=bool(gallery.is_published),
        published_at=gallery.published_at,
        created_at=gallery.created_at,
        photo_count=len(gallery.photos or []),
    )


def _to_detail(gallery) -> GalleryDetailResponse:
    base = _to_response(gallery)
    return GalleryDetailResponse(
        **base.model_dump(),
        photos=[PhotoResponse.model_validate(p) for p in (gallery.photos or [])],
    )


@team_router.post("", response_model=GalleryDetailResponse, status_code=201)
def create_gallery(
    event_id: int,
    payload: GalleryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin selects photos + sets PIN (SRD step 4, unpublished until published)."""
    ensure_event_admin(event_id, db, current_user)
    gallery = gallery_crud.create_gallery(db, event_id, payload)
    return _to_detail(gallery)


@team_router.get("", response_model=list[GalleryResponse])
def list_galleries(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.core.dependencies import ensure_event_access

    ensure_event_access(event_id, db, current_user)
    return [_to_response(g) for g in gallery_crud.get_galleries_by_event(db, event_id)]


@team_router.get("/{gallery_id}", response_model=GalleryDetailResponse)
def get_gallery(
    event_id: int,
    gallery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.core.dependencies import ensure_event_access

    ensure_event_access(event_id, db, current_user)
    gallery = gallery_crud.get_gallery(db, gallery_id)
    if gallery is None or int(gallery.event_id) != event_id:
        raise HTTPException(status_code=404, detail="Gallery not found")
    return _to_detail(gallery)


@team_router.put("/{gallery_id}", response_model=GalleryDetailResponse)
def update_gallery(
    event_id: int,
    gallery_id: int,
    payload: GalleryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_event_admin(event_id, db, current_user)
    gallery = gallery_crud.get_gallery(db, gallery_id)
    if gallery is None or int(gallery.event_id) != event_id:
        raise HTTPException(status_code=404, detail="Gallery not found")
    updated = gallery_crud.update_gallery(db, gallery_id, payload)
    assert updated is not None
    return _to_detail(updated)


@team_router.post("/{gallery_id}/publish", response_model=GalleryDetailResponse)
def publish_gallery(
    event_id: int,
    gallery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publish -> generates the shareable link + PIN credentials for the customer."""
    ensure_event_admin(event_id, db, current_user)
    gallery = gallery_crud.get_gallery(db, gallery_id)
    if gallery is None or int(gallery.event_id) != event_id:
        raise HTTPException(status_code=404, detail="Gallery not found")
    if not (gallery.photos or []):
        raise HTTPException(status_code=400, detail="Add photos before publishing")
    published = gallery_crud.publish_gallery(db, gallery_id)
    assert published is not None
    return _to_detail(published)


@team_router.post("/{gallery_id}/unpublish", response_model=GalleryDetailResponse)
def unpublish_gallery(
    event_id: int,
    gallery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_event_admin(event_id, db, current_user)
    gallery = gallery_crud.get_gallery(db, gallery_id)
    if gallery is None or int(gallery.event_id) != event_id:
        raise HTTPException(status_code=404, detail="Gallery not found")
    updated = gallery_crud.unpublish_gallery(db, gallery_id)
    assert updated is not None
    return _to_detail(updated)


@team_router.delete("/{gallery_id}", status_code=204)
def delete_gallery(
    event_id: int,
    gallery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_event_admin(event_id, db, current_user)
    gallery = gallery_crud.get_gallery(db, gallery_id)
    if gallery is None or int(gallery.event_id) != event_id:
        raise HTTPException(status_code=404, detail="Gallery not found")
    gallery_crud.delete_gallery(db, gallery_id)
    return None


# --- public customer routes (no account) ---
public_router = APIRouter(prefix="/public/galleries", tags=["public-gallery"])


@public_router.get("/{slug}/meta", response_model=dict)
def gallery_meta(slug: str, db: Session = Depends(get_db)):
    """Customer opens the link: reveal title/photo count, never photos or PIN."""
    gallery = gallery_crud.get_gallery_by_slug(db, slug)
    if gallery is None or not bool(gallery.is_published):
        raise HTTPException(status_code=404, detail="Gallery not found")
    event = db.query(Event).filter(Event.id == int(gallery.event_id)).first()
    return {
        "title": str(gallery.title),
        "slug": str(gallery.slug),
        "event_name": str(event.name) if event else "",
        "photo_count": len(gallery.photos or []),
    }


@public_router.post("/{slug}/photos", response_model=PublicGalleryResponse)
def gallery_photos_with_pin(
    slug: str,
    payload: GalleryPinVerify,
    db: Session = Depends(get_db),
):
    """Customer enters PIN -> published photos. Wrong PIN -> 401 (never leak)."""
    _check_pin_rate_limit(slug)
    gallery = gallery_crud.get_gallery_by_slug(db, slug)
    if gallery is None or not bool(gallery.is_published):
        _record_pin_attempt(slug, False)
        raise HTTPException(status_code=404, detail="Gallery not found")
    if not gallery.verify_pin(payload.pin):
        _record_pin_attempt(slug, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect PIN"
        )
    _record_pin_attempt(slug, True)
    event = db.query(Event).filter(Event.id == int(gallery.event_id)).first()
    return PublicGalleryResponse(
        title=str(gallery.title),
        slug=str(gallery.slug),
        event_name=str(event.name) if event else "",
        photos=[PhotoResponse.model_validate(p) for p in (gallery.photos or [])],
    )
