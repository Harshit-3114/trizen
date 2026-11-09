from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.gallery import Gallery
from app.models.photo import Photo
from app.schemas.gallery import GalleryCreate, GalleryUpdate


def _photo_ids_valid(db: Session, event_id: int, photo_ids: list[int]) -> list[int]:
    if not photo_ids:
        return []
    rows = (
        db.query(Photo.id)
        .filter(Photo.event_id == event_id, Photo.id.in_(photo_ids))
        .all()
    )
    valid = {r[0] for r in rows}
    return [pid for pid in photo_ids if pid in valid]


def get_gallery(db: Session, gallery_id: int) -> Gallery | None:
    return db.query(Gallery).filter(Gallery.id == gallery_id).first()


def get_gallery_by_slug(db: Session, slug: str) -> Gallery | None:
    return db.query(Gallery).filter(Gallery.slug == slug).first()


def get_galleries_by_event(db: Session, event_id: int) -> list[Gallery]:
    return (
        db.query(Gallery)
        .filter(Gallery.event_id == event_id)
        .order_by(Gallery.created_at.desc())
        .all()
    )


def create_gallery(db: Session, event_id: int, gallery: GalleryCreate) -> Gallery:
    db_gallery = Gallery(
        event_id=event_id,
        title=gallery.title,
        is_published=False,
    )
    db_gallery.set_pin(gallery.pin)
    db.add(db_gallery)
    db.commit()
    db.refresh(db_gallery)
    if gallery.photo_ids:
        valid_ids = _photo_ids_valid(db, event_id, gallery.photo_ids)
        photos = db.query(Photo).filter(Photo.id.in_(valid_ids)).all() if valid_ids else []
        db_gallery.photos = photos
        for photo in photos:
            setattr(photo, "is_selected", True)
        db.commit()
        db.refresh(db_gallery)
    return db_gallery


def update_gallery(db: Session, gallery_id: int, gallery: GalleryUpdate) -> Gallery | None:
    db_gallery = get_gallery(db, gallery_id)
    if not db_gallery:
        return None
    data = gallery.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None:
        db_gallery.title = data["title"]
    if data.get("pin"):
        db_gallery.set_pin(data["pin"])
    if data.get("photo_ids") is not None:
        valid_ids = _photo_ids_valid(db, int(db_gallery.event_id), data["photo_ids"])
        photos = db.query(Photo).filter(Photo.id.in_(valid_ids)).all() if valid_ids else []
        db_gallery.photos = photos
    if data.get("is_published") is not None:
        db_gallery.is_published = bool(data["is_published"])
        db_gallery.published_at = (
            datetime.now(timezone.utc) if data["is_published"] else None
        )
    db.commit()
    db.refresh(db_gallery)
    return db_gallery


def publish_gallery(db: Session, gallery_id: int) -> Gallery | None:
    db_gallery = get_gallery(db, gallery_id)
    if not db_gallery:
        return None
    db_gallery.is_published = True
    db_gallery.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_gallery)
    return db_gallery


def unpublish_gallery(db: Session, gallery_id: int) -> Gallery | None:
    db_gallery = get_gallery(db, gallery_id)
    if not db_gallery:
        return None
    db_gallery.is_published = False
    db_gallery.published_at = None
    db.commit()
    db.refresh(db_gallery)
    return db_gallery


def delete_gallery(db: Session, gallery_id: int) -> Gallery | None:
    db_gallery = get_gallery(db, gallery_id)
    if db_gallery:
        db.delete(db_gallery)
        db.commit()
    return db_gallery
