"""Criterion: Audit memakai identitas akun login.

The approval/reject decision must record the admin_name and admin_role from
the authenticated session, not any client-supplied value in the request body.
"""

import time

def test_audit_log_uses_session_identity_not_client_body(client, login_as):
    email = f"tscheck-audit-{int(time.time() * 1000)}@example.com"
    payload = {
        "buyer_type": "individual",
        "full_name": "Tscheck Audit Bidder",
        "email": email,
        "phone": "081234500011",
        "identity_number": "3201010101099901",
        "address": "Jl. Tscheck Audit No. 1",
    }
    created = client.post("/buyers/register", json=payload)
    assert created.status_code == 201, created.text
    buyer_id = created.json()["id"]

    file_bytes = b"%PDF-1.4 tscheck audit fixture pdf"
    uploaded = client.post(
        f"/buyers/{buyer_id}/documents",
        data={"document_type": "identity_document"},
        files={"file": ("ktp.pdf", file_bytes, "application/pdf")},
    )
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()["screening_status"] == "READY"

    rv_session = login_as(client, "reviewer", "MITReview!2026")
    rv_headers = {"Cookie": rv_session["cookie_header"]}
    session_name = rv_session["user"]["name"]
    session_role = rv_session["user"]["role"]

    # Client attempts to spoof a different admin identity in the request body.
    decision = client.patch(
        f"/admin/buyers/{buyer_id}",
        json={"verification_status": "APPROVED", "admin_name": "Spoofed Fake Admin", "reason": "ok"},
        headers=rv_headers,
    )
    assert decision.status_code == 200, decision.text

    logs = client.get("/admin/audit-logs", headers=rv_headers)
    assert logs.status_code == 200, logs.text
    matching = [entry for entry in logs.json() if entry["entity_id"] == buyer_id]
    assert len(matching) == 1, matching
    entry = matching[0]
    assert entry["admin_name"] == session_name, entry
    assert entry["admin_name"] != "Spoofed Fake Admin"
    assert entry["admin_role"] == session_role
