from sqlalchemy.orm import Session

from app.models.photo import Photo
from app.schemas.photo import PhotoCreate


def get_photo(db: Session, photo_id: int) -> Photo | None:
    return db.query(Photo).filter(Photo.id == photo_id).first()


def get_photos_by_event(
    db: Session,
    event_id: int,
    *,
    selected_only: bool = False,
    uploaded_by: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Photo]:
    q = db.query(Photo).filter(Photo.event_id == event_id)
    if selected_only:
        q = q.filter(Photo.is_selected.is_(True))
    if uploaded_by is not None:
        q = q.filter(Photo.uploaded_by == uploaded_by)
    return q.order_by(Photo.created_at.desc()).offset(skip).limit(min(limit, 200)).all()


def count_photos_by_event(db: Session, event_id: int, **filters) -> int:
    q = db.query(Photo).filter(Photo.event_id == event_id)
    if filters.get("selected_only"):
        q = q.filter(Photo.is_selected.is_(True))
    if filters.get("uploaded_by") is not None:
        q = q.filter(Photo.uploaded_by == filters["uploaded_by"])
    return q.count()


def create_photo(
    db: Session,
    *,
    event_id: int,
    uploaded_by: int,
    filename: str,
    storage_url: str,
    content_type: str,
    file_size: int,
) -> Photo:
    db_photo = Photo(
        event_id=event_id,
        uploaded_by=uploaded_by,
        filename=filename,
        storage_url=storage_url,
        content_type=content_type,
        file_size=file_size,
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def create_photo_from_schema(db: Session, photo: PhotoCreate, uploaded_by: int) -> Photo:
    return create_photo(
        db,
        event_id=photo.event_id,
        uploaded_by=uploaded_by,
        filename=photo.filename,
        storage_url=photo.storage_url,
        content_type=photo.content_type,
        file_size=photo.file_size,
    )


def set_photos_selected(db: Session, event_id: int, photo_ids: list[int], selected: bool) -> int:
    photos = (
        db.query(Photo)
        .filter(Photo.event_id == event_id, Photo.id.in_(photo_ids))
        .all()
    )
    for photo in photos:
        setattr(photo, "is_selected", selected)
    db.commit()
    return len(photos)


def delete_photo(db: Session, photo_id: int) -> Photo | None:
    db_photo = get_photo(db, photo_id)
    if db_photo:
        db.delete(db_photo)
        db.commit()
    return db_photo
