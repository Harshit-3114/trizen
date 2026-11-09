# Trizen Photo Sharing Platform

Full-stack photo-sharing app for photography/event teams: team uploads event
photos, the admin curates and publishes a **PIN-protected customer gallery**
accessible via a shareable link — no customer account needed.

Built for the **TrizenAI Full-Stack Internship Challenge**
(`TrizenAI_Full_Stack_Internship_Challenge.md`).

## Live demo

| Item | Value |
|---|---|
| Frontend | `http://localhost:3000` (deploy to Vercel/Netlify) |
| Backend API | `http://localhost:8000` (docs at `/docs`, health at `/health`) |
| Demo admin | `admin@trizen.demo` / `Admin@123` |
| Demo member | `member@trizen.demo` / `Member@123` |
| Demo gallery 1 | slug printed by `seed.py` + PIN `482917` (published) |
| Demo gallery 2 | slug printed by `seed.py` + PIN `239581` (published) |

> Fill in your deployed URLs before submitting to `talent@trizen-ai.com`.
> Never commit `.env` files or real credentials.

## Tech stack

- **Backend:** FastAPI, SQLAlchemy 2.0, Pydantic v2, JWT (`python-jose`) + bcrypt
- **DB:** SQLite for local dev (`trizen.db`); Postgres via `DATABASE_URL` in production
- **Storage:** local disk (`uploads/`) by default; S3-compatible (AWS S3 / Supabase
  Storage) via `STORAGE_BACKEND=s3` — only metadata lives in the DB, never image bytes
- **Frontend:** React 18 + TypeScript (CRA), React Router, Axios
- **Tests:** pytest + FastAPI TestClient (`backend/tests/test_api.py`)
- **Deploy:** Dockerfile (backend), Vercel/Netlify (frontend)

## Workflow (maps to SRD section 3)

1. **Admin** creates an event and adds team members by email.
2. **Team member** opens assigned events and uploads photos (multi-file).
3. **Admin** reviews all photos, ticks **Select** on keepers (`PATCH .../photos/select`).
4. **Admin** publishes a gallery with a numeric PIN → gets link `/gallery/<slug>` + PIN.
5. **Customer** opens the link, enters the PIN, views published photos. No account.

## System architecture

```
[ React SPA ] --HTTPS--> [ FastAPI /api/v1 ] --SQL--> [ Postgres / SQLite ]
      |                          |
      |                    [ Object storage ]
      |                    local uploads/ (dev)
      |                    S3 / Supabase (prod, STORAGE_BACKEND=s3)
      |
[ Customer gallery /gallery/:slug ] --PIN--> public endpoints (no auth)
```

### Database design

- `users(id, email unique, full_name, password_hash, role[admin|member], is_active, created_at)`
- `events(id, name, description, admin_id -> users, created_at)`
- `event_members(event_id, user_id)` composite PK — team assignment per event
- `photos(id, event_id -> events, uploaded_by -> users, filename, storage_url,
  content_type, file_size, is_selected, created_at)` — curation flag
- `galleries(id, event_id -> events, title, slug unique, pin_hash bcrypt,
  is_published, published_at, created_at)`
- `gallery_photos(gallery_id, photo_id)` — published photo set per gallery

Only **published** galleries expose photos, and only through the PIN endpoint.
Unpublished slugs return 404 (no existence leak); wrong PIN returns 401 with no data.

## API overview (`/api/v1`)

- Auth: `POST /auth/register`, `POST /auth/login` (OAuth2 form), `GET /auth/me`
- Events: `GET /events` (scoped: owned+assigned), `POST /events`,
  `GET|PUT|DELETE /events/{id}`
- Members: `GET /events/{id}/members`, `POST /events/{id}/members {email}`,
  `DELETE /events/{id}/members/{user_id}`
- Photos: `POST /events/{id}/photos` (multipart `files[]`, multi-upload),
  `GET /events/{id}/photos?page&page_size&selected_only&mine`,
  `PATCH /events/{id}/photos/select {photo_ids, selected}`,
  `DELETE /events/{id}/photos/{photo_id}`
- Team galleries: `POST|GET /events/{id}/galleries`,
  `GET|PUT /events/{id}/galleries/{gid}`,
  `POST .../{gid}/publish|unpublish`, `DELETE .../{gid}`
- Public (no auth): `GET /public/galleries/{slug}/meta`,
  `POST /public/galleries/{slug}/photos {pin}`

## Local setup

### Backend

```bat
cd backend
copy .env.example .env
REM set a long random SECRET_KEY in .env
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`. Or double-click `start.bat` from repo root.

### Frontend

```bat
cd frontend
npm install
echo REACT_APP_API_URL=http://localhost:8000/api/v1> .env
npm start
```

App: `http://localhost:3000`.

### Tests

```bat
cd backend
python -m pytest tests/test_api.py -v
```

Covers: auth + RBAC (incl. privilege-escalation block), event isolation +
membership, photo upload validation + select/delete access control, gallery
publish/unpublish + PIN verify (correct/wrong/unpublished).

## Environment variables

Backend (`backend/.env`, see `.env.example`): `APP_ENV`, `DATABASE_URL`,
`SECRET_KEY` (required in prod), `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`,
`STORAGE_BACKEND`, `UPLOAD_DIR`, `MAX_UPLOAD_MB`, `S3_BUCKET`, `S3_REGION`,
`S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`.

Frontend (`frontend/.env`): `REACT_APP_API_URL` (e.g. `http://localhost:8000/api/v1`).

## Deployment: all on Vercel + Neon (recommended)

1. **Database (Neon):** create a free Postgres project, copy the pooled
   connection string (`...?sslmode=require`).
2. **Photo storage:** Neon is database-only — create an S3-compatible bucket
   (Supabase Storage or Cloudflare R2) and note its endpoint + keys.
3. **Import to Vercel** (repo root; `vercel.json` builds the frontend and serves
   the API from `api/index.py` on the same domain, so no CORS setup needed).
   Environment variables:
   - `DATABASE_URL` = Neon pooled URL
   - `SECRET_KEY` = long random string (required)
   - `APP_ENV` = `production`
   - `STORAGE_BACKEND` = `s3`, plus `S3_BUCKET`, `S3_REGION`, `S3_ENDPOINT_URL`,
     `S3_ACCESS_KEY`, `S3_SECRET_KEY`
   - `REACT_APP_API_URL` = `/api/v1` (same-origin)
   - `MAX_UPLOAD_MB` = `4` (Vercel Hobby caps request bodies at ~4.5 MB)
4. **Seed production** once from your machine:
   `cd backend && DATABASE_URL="<neon-url>" SECRET_KEY="<same-secret>" python seed.py`
5. Open `/docs` on your deployment to verify, then fill the Live demo table below.

Alternative: backend on Railway/Render via `backend/Dockerfile` (persistent disk,
no payload caps) + frontend on Vercel.

## Deployment (generic notes)

- **Backend (Railway/Render/Fly):** build `backend/`, start
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; set `DATABASE_URL` (Postgres),
  `SECRET_KEY`, `CORS_ORIGINS` (frontend URL), `STORAGE_BACKEND=s3` + bucket creds
  for real object storage. `Dockerfile` provided (`docker build ./backend`).
- **Frontend (Vercel):** root `frontend/`, set `REACT_APP_API_URL` to the deployed
  API (`https://<api>/api/v1`), `npm run build`.
- Run `python seed.py` once: creates demo admin/member, 3 mock events with 20 sample photos, 2 published galleries + 1 draft. Gallery slugs print at the end.

## Security practices

- bcrypt password + PIN hashing; JWT auth on all team routes; public routes are
  PIN-gated with per-slug rate limiting (20 attempts / 10 min).
- Event data never leaks: non-members get `404`, not `403`, on foreign events.
- Members cannot publish galleries, select photos, or delete others photos.
- Upload validation: image MIME allowlist, 10 MB default cap, 50 files/request.
- `SECRET_KEY` from env; `.env` files git-ignored; error handler hides internals
  outside development.

## Known limitations

- Local storage serves via `/uploads` (use CDN/S3 in production).
- No thumbnails/resizing, search, or gallery expiry yet (listed SRD bonus items).
- SQLite default is single-node; use Postgres (`DATABASE_URL`) when deploying.
- Fresh databases are created automatically on startup (`create_all`). Note that
  `create_all` only creates missing tables — it never alters existing ones — so
  schema changes to an existing production database need a manual migration.
