"""Criterion: Peserta tidak lengkap tidak masuk antrean review.

Registration without documents -> INCOMPLETE / screening INCOMPLETE, and does
not appear in /admin/buyers?status=PENDING (which only returns screening READY).
"""

import time

import pytest


@pytest.fixture
def unique_email():
    return f"tscheck-incomplete-{int(time.time() * 1000)}@example.com"


def test_registration_without_documents_is_incomplete(client, unique_email, login_as):
    payload = {
        "buyer_type": "individual",
        "full_name": "Tscheck Incomplete Bidder",
        "email": unique_email,
        "phone": "081234567890",
        "identity_number": "3201010101010001",
        "address": "Jl. Tscheck Testing No. 1",
    }
    resp = client.post("/buyers/register", json=payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["verification_status"] == "INCOMPLETE"
    assert body["screening_status"] == "INCOMPLETE"
    assert "identity_document" not in {d.get("document_type") for d in body["documents"]}

    session = login_as(client, "superadmin", "LelangOto!2026")
    pending = client.get("/admin/buyers", params={"status": "PENDING"}, headers={"Cookie": session["cookie_header"]})
    assert pending.status_code == 200
    pending_ids = {b["id"] for b in pending.json()}
    assert body["id"] not in pending_ids
