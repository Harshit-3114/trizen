from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.crud.gallery import get_gallery, create_gallery, update_gallery, delete_gallery, get_galleries_by_event, get_gallery_by_slug
from app.schemas.gallery import GalleryCreate, GalleryResponse, GalleryPinVerify
from app.schemas.user import UserResponse
from app.models.event import Event

router = APIRouter(prefix="/galleries", tags=["galleries"])

@router.post("/events/{event_id}", response_model=GalleryResponse)
def create_gallery_for_event(
    event_id: int,
    gallery: GalleryCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    # Verify event exists and user is admin
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.admin_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create gallery for this event")
    return create_gallery(db, gallery)

@router.get("", response_model=list[GalleryResponse])
def read_galleries_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    # Verify event exists and user is admin
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.admin_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view galleries for this event")
    return get_galleries_by_event(db, event_id)

@router.get("/{slug}", response_model=GalleryResponse)
def read_gallery_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    gallery = get_gallery_by_slug(db, slug)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    return gallery

@router.post("/{slug}/pin", response_model=dict)
def verify_gallery_pin(
    slug: str,
    pin_data: GalleryPinVerify,
    db: Session = Depends(get_db)
):
    gallery = get_gallery_by_slug(db, slug)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    if gallery.verify_pin(pin_data.pin):
        return {"message": "PIN verified successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid PIN")

@router.put("/{gallery_id}", response_model=GalleryResponse)
def update_gallery_endpoint(
    gallery_id: int,
    gallery: GalleryCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    db_gallery = update_gallery(db, gallery_id, gallery)
    if not db_gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    # Verify user is admin of the event
    event = db.query(Event).filter(Event.id == db_gallery.event_id).first()
    if not event or event.admin_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this gallery")
    return db_gallery

@router.delete("/{gallery_id}")
def delete_gallery_endpoint(
    gallery_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user)
):
    db_gallery = delete_gallery(db, gallery_id)
    if not db_gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    # Verify user is admin of the event
    event = db.query(Event).filter(Event.id == db_gallery.event_id).first()
    if not event or event.admin_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this gallery")
    return {"message": "Gallery deleted successfully"}