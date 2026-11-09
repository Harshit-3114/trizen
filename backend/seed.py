"""Seed demo data: users, mock events with real photos, galleries. Idempotent.

Usage:
    python seed.py

Creates (if missing):
  - admin@trizen.demo / Admin@123 (admin) and member@trizen.demo / Member@123
  - 3 mock events with downloadable sample photos (picsum.photos)
  - published customer galleries with known PINs (printed at the end)
"""

import urllib.request
import uuid
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.crud import gallery as gallery_crud
from app.crud import photo as photo_crud
from app.crud.user import create_user, get_user_by_email
from app.models import Base
from app.models.event import Event
from app.models.event_member import event_member
from app.schemas.gallery import GalleryCreate, GalleryUpdate
from app.schemas.user import UserCreate

ADMIN = ("admin@trizen.demo", "Admin Lead", "Admin@123", "admin")
MEMBER = ("member@trizen.demo", "Team Member", "Member@123", "member")

MOCK_EVENTS = [
    {
        "name": "Arjun & Priya Wedding",
        "description": "Three-day wedding celebration at Udaipur Palace.",
        "photo_count": 8,
        "select_count": 5,
        "gallery": {"title": "Demo Highlights", "pin": "482917", "publish": True},
    },
    {
        "name": "Meera & Kabir Sangeet",
        "description": "Sangeet night full of music, dance and family performances.",
        "photo_count": 6,
        "select_count": 4,
        "gallery": {"title": "Sangeet Highlights", "pin": "239581", "publish": True},
    },
    {
        "name": "TechNova Annual Gala 2026",
        "description": "Corporate awards night. Curation still in progress.",
        "photo_count": 6,
        "select_count": 0,
        "gallery": {"title": "Gala Drafts", "pin": "774902", "publish": False},
    },
]


def ensure_user(db, email, full_name, password, role):
    user = get_user_by_email(db, email)
    if user:
        return user
    return create_user(
        db, UserCreate(email=email, full_name=full_name, password=password, role=role)
    )


def ensure_membership(db, event_id, user_id):
    exists = db.execute(
        select(event_member).where(
            event_member.c.event_id == event_id,
            event_member.c.user_id == user_id,
        )
    ).first()
    if not exists:
        db.execute(event_member.insert().values(event_id=event_id, user_id=user_id))
        db.commit()


def download_sample(seed, dest):
    url = f"https://picsum.photos/seed/{seed}/1200/800"
    req = urllib.request.Request(url, headers={"User-Agent": "trizen-seed/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return len(data)


def ensure_photos(db, event, count, select_count, tag):
    existing = photo_crud.get_photos_by_event(db, int(event.id))
    if len(existing) >= count:
        return existing
    created = list(existing)
    upload_root = Path(settings.UPLOAD_DIR) / f"event_{int(event.id)}"
    upload_root.mkdir(parents=True, exist_ok=True)
    needed = count - len(existing)
    for i in range(needed):
        idx = len(existing) + i + 1
        fname = f"{uuid.uuid4().hex}.jpg"
        dest = upload_root / fname
        try:
            size = download_sample(f"trizen-{tag}-{idx}", dest)
        except Exception as exc:
            print(f"  photo download failed ({exc}); skipping rest for this event")
            break
        photo = photo_crud.create_photo(
            db,
            event_id=int(event.id),
            uploaded_by=int(event.admin_id),
            filename=f"sample-{idx}.jpg",
            storage_url=f"/uploads/event_{int(event.id)}/{fname}",
            content_type="image/jpeg",
            file_size=size,
        )
        created.append(photo)
        print(f"  + photo {photo.id} ({size} bytes)")
    if select_count and created:
        ids = [int(p.id) for p in created[:select_count]]
        photo_crud.set_photos_selected(db, int(event.id), ids, True)
        print(f"  selected {len(ids)} photos")
    return created


def ensure_gallery(db, event_id, spec, photos):
    galleries = gallery_crud.get_galleries_by_event(db, event_id)
    gallery = next((g for g in galleries if str(g.title) == spec["title"]), None)
    if gallery is None:
        selected_ids = [int(p.id) for p in photos if bool(p.is_selected)]
        gallery = gallery_crud.create_gallery(
            db,
            event_id,
            GalleryCreate(title=spec["title"], pin=spec["pin"], photo_ids=selected_ids),
        )
        print(f"  gallery '{gallery.title}' slug={gallery.slug}")
    elif not (gallery.photos or []) and photos:
        selected_ids = [int(p.id) for p in photos if bool(p.is_selected)]
        if selected_ids:
            gallery_crud.update_gallery(
                db, int(gallery.id), GalleryUpdate(photo_ids=selected_ids)
            )
            db.refresh(gallery)
    if spec["publish"] and not bool(gallery.is_published):
        gallery_crud.publish_gallery(db, int(gallery.id))
        db.refresh(gallery)
    return gallery


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = ensure_user(db, *ADMIN)
        member = ensure_user(db, *MEMBER)
        print("Seed: users ready.")
        for n, spec in enumerate(MOCK_EVENTS, start=1):
            print(f"Event: {spec['name']}")
            event = db.query(Event).filter(Event.name == spec["name"]).first()
            if not event:
                event = Event(
                    name=spec["name"],
                    description=spec["description"],
                    admin_id=int(admin.id),
                )
                db.add(event)
                db.commit()
                db.refresh(event)
            ensure_membership(db, int(event.id), int(member.id))
            photos = ensure_photos(
                db, event, spec["photo_count"], spec["select_count"], f"mock{n}"
            )
            gallery = ensure_gallery(db, int(event.id), spec["gallery"], photos)
            state = "PUBLISHED" if bool(gallery.is_published) else "draft"
            print(f"  -> event {int(event.id)} [{state}] gallery /gallery/{gallery.slug}")
        print("Seed complete.")
        print(f"Admin:  {ADMIN[0]} / {ADMIN[2]}")
        print(f"Member: {MEMBER[0]} / {MEMBER[2]}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
