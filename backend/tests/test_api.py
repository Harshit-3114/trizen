import io
import os
import tempfile

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_api.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-123456")
os.environ.setdefault("APP_ENV", "test")

from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.core.database import engine  # noqa: E402


def _client():
    # fresh db per module run
    for f in ("test_api.db",):
        try:
            os.remove(f)
        except FileNotFoundError:
            pass
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


client = _client()


def _register(email, password, full_name="Test User", role="member"):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": full_name, "password": password, "role": role},
    )
    assert r.status_code in (200, 201), r.text
    return r.json()


def _login(email, password):
    r = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_auth_and_rbac():
    admin = _register("admin1@t.t", "Admin1234", "Admin One", "admin")
    assert admin["role"] == "admin"  # first user bootstraps admin
    member = _register("member1@t.t", "Member1234", "Member One", "member")
    assert member["role"] == "member"
    # privilege escalation blocked: later admin self-registration coerced to member
    evil = _register("evil@t.t", "Evil1234", "Evil", "admin")
    assert evil["role"] == "member"

    admin_tok = _login("admin1@t.t", "Admin1234")
    # wrong password
    r = client.post("/api/v1/auth/login", data={"username": "admin1@t.t", "password": "nope"})
    assert r.status_code == 401
    # me
    r = client.get("/api/v1/auth/me", headers=_auth(admin_tok))
    assert r.status_code == 200 and r.json()["email"] == "admin1@t.t"


def test_event_isolation_and_membership():
    admin_tok = _login("admin1@t.t", "Admin1234")
    member_tok = _login("member1@t.t", "Member1234")
    outsider = _register("outsider@t.t", "Outsider1", "Outsider", "member")
    outsider_tok = _login("outsider@t.t", "Outsider1")

    r = client.post(
        "/api/v1/events",
        json={"name": "Iso Event", "description": "d"},
        headers=_auth(admin_tok),
    )
    assert r.status_code == 201, r.text
    event_id = r.json()["id"]

    # outsider cannot see it (404, not 403 -> no existence leak)
    r = client.get(f"/api/v1/events/{event_id}", headers=_auth(outsider_tok))
    assert r.status_code == 404
    # member cannot see before assignment
    r = client.get("/api/v1/events", headers=_auth(member_tok))
    assert all(e["id"] != event_id for e in r.json())
    # admin adds member by email
    r = client.post(
        f"/api/v1/events/{event_id}/members",
        json={"email": "member1@t.t"},
        headers=_auth(admin_tok),
    )
    assert r.status_code == 201, r.text
    # now member sees it
    r = client.get(f"/api/v1/events/{event_id}", headers=_auth(member_tok))
    assert r.status_code == 200
    # member cannot add members
    r = client.post(
        f"/api/v1/events/{event_id}/members",
        json={"email": "outsider@t.t"},
        headers=_auth(member_tok),
    )
    assert r.status_code == 403


def _png_bytes(color=(255, 0, 0)):
    # minimal valid PNG (1x1) without Pillow
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def test_photo_upload_select_and_access_control():
    admin_tok = _login("admin1@t.t", "Admin1234")
    member_tok = _login("member1@t.t", "Member1234")
    events = client.get("/api/v1/events", headers=_auth(admin_tok)).json()
    event_id = events[0]["id"]

    # member uploads 2 photos (multipart, multi-file)
    files = [
        ("files", ("a.png", io.BytesIO(_png_bytes()), "image/png")),
        ("files", ("b.png", io.BytesIO(_png_bytes()), "image/png")),
    ]
    r = client.post(
        f"/api/v1/events/{event_id}/photos", files=files, headers=_auth(member_tok)
    )
    assert r.status_code == 201, r.text
    assert len(r.json()) == 2
    photo_ids = [p["id"] for p in r.json()]

    # invalid type rejected
    r = client.post(
        f"/api/v1/events/{event_id}/photos",
        files=[("files", ("x.txt", io.BytesIO(b"hello"), "text/plain"))],
        headers=_auth(member_tok),
    )
    assert r.status_code == 415

    # member cannot select (publish path); admin can
    r = client.patch(
        f"/api/v1/events/{event_id}/photos/select",
        json={"photo_ids": photo_ids[:1], "selected": True},
        headers=_auth(member_tok),
    )
    assert r.status_code == 403
    r = client.patch(
        f"/api/v1/events/{event_id}/photos/select",
        json={"photo_ids": photo_ids[:1], "selected": True},
        headers=_auth(admin_tok),
    )
    assert r.status_code == 200 and r.json()["updated"] == 1

    # member CAN delete own photo
    r = client.delete(
        f"/api/v1/events/{event_id}/photos/{photo_ids[1]}", headers=_auth(member_tok)
    )
    assert r.status_code == 204, r.text


def test_gallery_publish_and_pin_flow():
    admin_tok = _login("admin1@t.t", "Admin1234")
    member_tok = _login("member1@t.t", "Member1234")
    events = client.get("/api/v1/events", headers=_auth(admin_tok)).json()
    event_id = events[0]["id"]
    photos = client.get(
        f"/api/v1/events/{event_id}/photos", headers=_auth(admin_tok)
    ).json()
    assert photos["total"] >= 1
    pid = photos["items"][0]["id"]

    # member cannot publish
    r = client.post(
        f"/api/v1/events/{event_id}/galleries",
        json={"title": "Nope", "pin": "111111", "photo_ids": [pid]},
        headers=_auth(member_tok),
    )
    assert r.status_code == 403

    # admin creates unpublished gallery
    r = client.post(
        f"/api/v1/events/{event_id}/galleries",
        json={"title": "Wedding Highlights", "pin": "482917", "photo_ids": [pid]},
        headers=_auth(admin_tok),
    )
    assert r.status_code == 201, r.text
    slug = r.json()["slug"]
    gid = r.json()["id"]
    assert r.json()["is_published"] is False

    # unpublished -> customer gets 404 (no leak)
    r = client.get(f"/api/v1/public/galleries/{slug}/meta")
    assert r.status_code == 404

    # publish
    r = client.post(
        f"/api/v1/events/{event_id}/galleries/{gid}/publish", headers=_auth(admin_tok)
    )
    assert r.status_code == 200 and r.json()["is_published"] is True

    # wrong PIN -> 401, no photos leaked
    r = client.post(f"/api/v1/public/galleries/{slug}/photos", json={"pin": "000000"})
    assert r.status_code == 401
    assert "photos" not in r.json()

    # correct PIN -> photos
    r = client.post(f"/api/v1/public/galleries/{slug}/photos", json={"pin": "482917"})
    assert r.status_code == 200, r.text
    assert len(r.json()["photos"]) >= 1

    # unpublish hides again
    r = client.post(
        f"/api/v1/events/{event_id}/galleries/{gid}/unpublish", headers=_auth(admin_tok)
    )
    assert r.status_code == 200
    r = client.post(f"/api/v1/public/galleries/{slug}/photos", json={"pin": "482917"})
    assert r.status_code == 404
