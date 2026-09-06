from sqlalchemy.orm import Session
from app.models.gallery import Gallery
from app.schemas.gallery import GalleryCreate

def get_gallery(db: Session, gallery_id: int):
    return db.query(Gallery).filter(Gallery.id == gallery_id).first()

def get_gallery_by_slug(db: Session, slug: str):
    return db.query(Gallery).filter(Gallery.slug == slug).first()

def get_galleries_by_event(db: Session, event_id: int):
    return db.query(Gallery).filter(Gallery.event_id == event_id).all()

def create_gallery(db: Session, gallery: GalleryCreate):
    db_gallery = Gallery(**gallery.dict(exclude={'pin'}))
    db_gallery.set_pin(gallery.pin)
    db.add(db_gallery)
    db.commit()
    db.refresh(db_gallery)
    return db_gallery

def update_gallery(db: Session, gallery_id: int, gallery: GalleryCreate):
    db_gallery = get_gallery(db, gallery_id)
    if db_gallery:
        for key, value in gallery.dict(exclude={'pin'}).items():
            setattr(db_gallery, key, value)
        if 'pin' in gallery.dict() and gallery.pin:
            db_gallery.set_pin(gallery.pin)
        db.commit()
        db.refresh(db_gallery)
    return db_gallery

def delete_gallery(db: Session, gallery_id: int):
    db_gallery = get_gallery(db, gallery_id)
    if db_gallery:
        db.delete(db_gallery)
        db.commit()
    return db_gallery