"""Auction sessions run Tue/Fri 10.00-15.00 WIB, publish H-3, and carry lot_ids; the public
catalog of sessions only ever exposes already-published sessions.
"""

from datetime import datetime, timedelta

import httpx


def test_admin_sessions_have_biweekly_schedule_and_lot_ids(client: httpx.Client, login_as):
    admin = login_as(client, "superadmin", "MITAuction!2026")
    resp = client.get("/admin/sessions", headers={"Cookie": admin["cookie_header"]})
    assert resp.status_code == 200, resp.text
    sessions = resp.json()
    assert len(sessions) > 0

    for session in sessions:
        start = datetime.fromisoformat(session["start_at"])
        end = datetime.fromisoformat(session["end_at"])
        publication = datetime.fromisoformat(session["publication_at"])
        assert start.weekday() in (1, 4), f"session {session['code']} not Tue/Fri: weekday={start.weekday()}"
        assert (end - start) == timedelta(hours=5), f"session {session['code']} window is not 10:00-15:00 (5h): {end - start}"
        assert (start - publication).days == 3, f"session {session['code']} publication_at is not H-3: {(start - publication).days} days"
        assert isinstance(session["lot_ids"], list)


def test_public_catalog_hides_unpublished_sessions(client: httpx.Client, login_as):
    admin = login_as(client, "superadmin", "MITAuction!2026")
    admin_sessions = client.get("/admin/sessions", headers={"Cookie": admin["cookie_header"]}).json()

    public_sessions = client.get("/sessions")
    assert public_sessions.status_code == 200, public_sessions.text
    public_ids = {s["id"] for s in public_sessions.json()}

    now = datetime.utcnow()
    unpublished = [s for s in admin_sessions if datetime.fromisoformat(s["publication_at"]) > now or s["status"] not in ("PUBLISHED", "LIVE", "CLOSED")]
    for session in unpublished:
        assert session["id"] not in public_ids, f"unpublished session {session['code']} leaked into public catalog"

    published = [s for s in admin_sessions if datetime.fromisoformat(s["publication_at"]) <= now and s["status"] in ("PUBLISHED", "LIVE", "CLOSED")]
    for session in published:
        assert session["id"] in public_ids, f"published session {session['code']} missing from public catalog"
