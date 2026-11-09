from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints import auth, events, gallery, memberships, photos
from app.core.config import settings
from app.core.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Photography/event team photo sharing: upload, curate, publish PIN galleries.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if settings.APP_ENV == "development":
        raise exc
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["ops"])
def health():
    return {"status": "ok", "env": settings.APP_ENV}


API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(memberships.router, prefix=API_PREFIX)
app.include_router(photos.router, prefix=API_PREFIX)
app.include_router(gallery.team_router, prefix=API_PREFIX)
app.include_router(gallery.public_router, prefix=API_PREFIX)

upload_root = Path(settings.UPLOAD_DIR)
upload_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_root)), name="uploads")
