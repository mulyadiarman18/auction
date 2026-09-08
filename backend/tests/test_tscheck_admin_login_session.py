"""Criterion: Admin route dilindungi login nyata.

/api/admin/lots requires an authenticated session; valid superadmin
credentials create a session (verified via /admin/auth/me), and invalid
credentials are rejected.
"""

def test_unauthenticated_request_is_rejected(client):
    resp = client.get("/admin/lots")
    assert resp.status_code in (401, 403), resp.text


def test_valid_login_creates_session_and_grants_access(client, login_as):
    session = login_as(client, "superadmin", "MITAuction!2026")
    assert session["user"]["role"] == "super_admin"
    headers = {"Cookie": session["cookie_header"]}

    me = client.get("/admin/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    assert me.json()["username"] == "superadmin"

    lots = client.get("/admin/lots", headers=headers)
    assert lots.status_code == 200, lots.text
    assert len(lots.json()) > 0


def test_invalid_credentials_are_rejected(client):
    resp = client.post("/admin/auth/login", json={"username": "superadmin", "password": "WrongPassword123"})
    assert resp.status_code in (401, 403, 422), resp.text
    assert "session" not in "".join(resp.cookies.keys())
