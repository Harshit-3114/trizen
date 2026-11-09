"""Object/file storage abstraction.

Default backend is local disk (``UPLOAD_DIR``), which satisfies the SRD rule
"do not store image files in the database" for local dev and small deploys.
Set ``STORAGE_BACKEND=s3`` plus S3_* settings to use AWS S3 or any
S3-compatible store (Supabase Storage exposes an S3 endpoint).

Only the metadata (filename, storage_url, file_size, content_type) is stored
in the database; bytes always live in object/file storage.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
}


def _upload_root() -> Path:
    root = Path(settings.UPLOAD_DIR)
    root.mkdir(parents=True, exist_ok=True)
    return root


def validate_upload(filename: str | None, content_type: str | None, size: int) -> str:
    if not content_type or content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{content_type}'. Allowed: jpeg, png, webp, heic.",
        )
    if size <= 0:
        raise HTTPException(status_code=400, detail=f"Empty file rejected: {filename or 'upload'}")
    if size > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {settings.MAX_UPLOAD_MB} MB): {filename or 'upload'}",
        )
    ext = ALLOWED_CONTENT_TYPES[content_type]
    return ext


async def save_upload(file: UploadFile, event_id: int) -> dict:
    """Persist one uploaded image; return metadata for the Photo row."""
    content = await file.read()
    size = len(content)
    ext = validate_upload(file.filename, file.content_type, size)

    if settings.STORAGE_BACKEND.lower() == "s3":
        return _save_to_s3(file, content, size, ext, event_id)

    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = _upload_root() / f"event_{event_id}" / safe_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return {
        "filename": file.filename or safe_name,
        "storage_url": f"/uploads/event_{event_id}/{safe_name}",
        "content_type": file.content_type or "image/jpeg",
        "file_size": size,
    }


def _save_to_s3(
    file: UploadFile, content: bytes, size: int, ext: str, event_id: int
) -> dict:
    try:
        import boto3  # optional dependency, only needed for s3 backend
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail="S3 backend selected but boto3 is not installed"
        ) from exc

    bucket = settings.S3_BUCKET or settings.SUPABASE_BUCKET
    if not bucket:
        raise HTTPException(status_code=500, detail="S3 bucket is not configured")
    key = f"event_{event_id}/{uuid.uuid4().hex}{ext}"
    client_kwargs: dict = {}
    if settings.S3_REGION:
        client_kwargs["region_name"] = settings.S3_REGION
    if settings.S3_ENDPOINT_URL:
        client_kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY or None,
        aws_secret_access_key=settings.S3_SECRET_KEY or None,
        **client_kwargs,
    )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=content,
        ContentType=file.content_type or "image/jpeg",
    )
    base = settings.S3_ENDPOINT_URL.rstrip("/") if settings.S3_ENDPOINT_URL else (
        f"https://{bucket}.s3.{settings.S3_REGION}.amazonaws.com" if settings.S3_REGION else f"s3://{bucket}"
    )
    return {
        "filename": file.filename or key.rsplit("/", 1)[-1],
        "storage_url": f"{base}/{key}",
        "content_type": file.content_type or "image/jpeg",
        "file_size": size,
    }
