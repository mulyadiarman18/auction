"""Criterion: Admin dapat mengunduh dokumen peserta.

Register a buyer, upload an identity document, then download it via the admin
endpoint and confirm the returned bytes/content-type match what was uploaded.
"""

import time


def test_admin_can_download_uploaded_document(client):
    email = f"tscheck-download-{int(time.time() * 1000)}@example.com"
    payload = {
        "buyer_type": "individual",
        "full_name": "Tscheck Download Bidder",
        "email": email,
        "phone": "081298765432",
        "identity_number": "3201010101010002",
        "address": "Jl. Tscheck Download No. 2",
    }
    created = client.post("/buyers/register", json=payload)
    assert created.status_code == 201, created.text
    buyer_id = created.json()["id"]

    file_bytes = b"%PDF-1.4 fake pdf content for tscheck"
    files = {"file": ("ktp.pdf", file_bytes, "application/pdf")}
    data = {"document_type": "identity_document"}
    uploaded = client.post(f"/buyers/{buyer_id}/documents", data=data, files=files)
    assert uploaded.status_code == 200, uploaded.text
    body = uploaded.json()
    assert body["verification_status"] == "PENDING"
    documents = body["documents"]
    assert len(documents) == 1
    document_id = documents[0]["id"]

    download = client.get(f"/admin/buyers/{buyer_id}/documents/{document_id}", params={"admin_role": "reviewer"})
    assert download.status_code == 200, download.text
    assert download.content == file_bytes
    assert download.headers["content-type"] == "application/pdf"
