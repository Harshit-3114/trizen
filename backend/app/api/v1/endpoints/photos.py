from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import ensure_event_access, ensure_event_admin
from app.core.security import get_current_user
from app.core.storage import save_upload
from app.crud import photo as photo_crud
from app.models.user import User
from app.schemas.photo import PhotoListResponse, PhotoResponse, PhotoSelect

router = APIRouter(prefix="/events/{event_id}/photos", tags=["photos"])


@router.post("", response_model=list[PhotoResponse], status_code=201)
async def upload_photos(
    event_id: int,
    files: list[UploadFile],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Multi-file upload. Team members upload to assigned events; admins to owned."""
    ensure_event_access(event_id, db, current_user)
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Max 50 files per request")
    created: list[PhotoResponse] = []
    for upload in files:
        try:
            meta = await save_upload(upload, event_id)
        except HTTPException:
            raise
        except Exception as exc:  # failed upload -> 422 with filename context
            raise HTTPException(
                status_code=422, detail=f"Failed to store {upload.filename}: {exc}"
            ) from exc
        photo = photo_crud.create_photo(
            db,
            event_id=event_id,
            uploaded_by=int(current_user.id),
            filename=meta["filename"],
            storage_url=meta["storage_url"],
            content_type=meta["content_type"],
            file_size=meta["file_size"],
        )
        created.append(PhotoResponse.model_validate(photo))
    return created


@router.get("", response_model=PhotoListResponse)
def list_photos(
    event_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(48, ge=1, le=200),
    selected_only: bool = False,
    mine: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Paginated photos. Members see event photos; `mine` filters own uploads."""
    ensure_event_access(event_id, db, current_user)
    uploaded_by = int(current_user.id) if mine and str(current_user.role) != "admin" else None
    # Admins may also filter; members viewing others photos is allowed within
    # an assigned event (they collaborate), but deletes stay restricted.
    skip = (page - 1) * page_size
    items = photo_crud.get_photos_by_event(
        db, event_id,
        selected_only=selected_only, uploaded_by=uploaded_by,
        skip=skip, limit=page_size,
    )
    total = photo_crud.count_photos_by_event(
        db, event_id,
        selected_only=selected_only, uploaded_by=uploaded_by,
    )
    return PhotoListResponse(
        items=[PhotoResponse.model_validate(p) for p in items],
        total=total, page=page, page_size=page_size,
    )


@router.patch("/select", response_model=dict)
def select_photos(
    event_id: int,
    payload: PhotoSelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin curates which photos go into the gallery (SRD step 3)."""
    ensure_event_admin(event_id, db, current_user)
    count = photo_crud.set_photos_selected(db, event_id, payload.photo_ids, payload.selected)
    return {"updated": count, "selected": payload.selected}


@router.delete("/{photo_id}", status_code=204)
def delete_photo(
    event_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Uploader may delete own photo; event admin may delete any (members cannot
    manage other users photos per SRD)."""
    photo = photo_crud.get_photo(db, photo_id)
    if photo is None or int(photo.event_id) != event_id:
        raise HTTPException(status_code=404, detail="Photo not found")
    ensure_event_access(event_id, db, current_user)
    is_owner = int(photo.uploaded_by) == int(current_user.id)
    try:
        ensure_event_admin(event_id, db, current_user)
        is_admin = True
    except HTTPException:
        is_admin = False
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the uploader or event admin can delete this photo",
        )
    photo_crud.delete_photo(db, photo_id)
    return None
