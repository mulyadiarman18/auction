"""Buyer P0 gate end-to-end: register -> approve -> membership fee -> deposit -> bid eligible.

Uses a self-contained tscheck- buyer fixture (never touches seeded Budi/Siti rows) and drives
the full pipeline through the real HTTP API: registration screening, reviewer approval,
finance membership confirmation, finance deposit confirmation, then a real bid placement.
"""

import io
import uuid

import httpx


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:10]


def test_buyer_p0_gate_end_to_end(client: httpx.Client, login_as):
    suffix = _unique_suffix()
    full_name = f"tscheck-buyer-p0-{suffix}"
    email = f"tscheck-p0-{suffix}@example.com"

    # 1. Register buyer -> INCOMPLETE (no documents yet)
    register_resp = client.post(
        "/buyers/register",
        json={
            "buyer_type": "individual",
            "full_name": full_name,
            "email": email,
            "phone": "081200000111",
            "identity_number": f"31740000{suffix[:8]}",
            "address": "Jakarta Timur, tscheck fixture",
        },
    )
    assert register_resp.status_code == 201, register_resp.text
    buyer = register_resp.json()
    buyer_id = buyer["id"]
    assert buyer["verification_status"] == "INCOMPLETE"

    # 2. Upload identity document -> screening READY, verification PENDING
    doc_resp = client.post(
        f"/buyers/{buyer_id}/documents",
        data={"document_type": "identity_document"},
        files={"file": ("ktp.png", io.BytesIO(b"fake-image-bytes"), "image/png")},
    )
    assert doc_resp.status_code == 200, doc_resp.text
    assert doc_resp.json()["verification_status"] == "PENDING"

    # Bid must be rejected before any approval at all
    early_bid = client.post("/lots/lot-001/bids", json={"bidder_name": full_name, "bidder_type": "individual", "amount": 999_999_999_999})
    assert early_bid.status_code == 403, early_bid.text

    # 3. Reviewer approves legality
    reviewer = login_as(client, "reviewer", "MITReview!2026")
    approve_resp = client.patch(
        f"/admin/buyers/{buyer_id}",
        json={"verification_status": "APPROVED", "admin_name": reviewer["user"]["name"], "reason": "tscheck fixture approved"},
        headers={"Cookie": reviewer["cookie_header"]},
    )
    assert approve_resp.status_code == 200, approve_resp.text
    assert approve_resp.json()["verification_status"] == "APPROVED"

    finance = login_as(client, "finance", "MITFinance!2026")

    # 4. Membership fee: upload proof, finance confirms -> ACTIVE + CONFIRMED
    membership_proof = client.post(
        f"/membership/buyers/{buyer_id}/proof",
        files={"file": ("membership.png", io.BytesIO(b"fake-membership-proof"), "image/png")},
    )
    assert membership_proof.status_code == 200, membership_proof.text
    assert membership_proof.json()["membership_payment_status"] == "PENDING"

    confirm_membership = client.patch(
        f"/admin/member-payments/{buyer_id}",
        json={"status": "CONFIRMED", "reason": "tscheck membership confirmed"},
        headers={"Cookie": finance["cookie_header"]},
    )
    assert confirm_membership.status_code == 200, confirm_membership.text
    confirmed = confirm_membership.json()
    assert confirmed["membership_payment_status"] == "CONFIRMED"
    assert confirmed["membership_status"] == "ACTIVE"

    # Bid still rejected: deposit not yet confirmed
    mid_bid = client.post("/lots/lot-001/bids", json={"bidder_name": full_name, "bidder_type": "individual", "amount": 999_999_999_999})
    assert mid_bid.status_code == 403, mid_bid.text

    # 5. Deposit Rp3.000.000: upload proof, finance confirms -> CONFIRMED
    deposit_proof = client.post(
        f"/deposits/buyers/{buyer_id}/proof",
        files={"file": ("deposit.png", io.BytesIO(b"fake-deposit-proof"), "image/png")},
    )
    assert deposit_proof.status_code == 200, deposit_proof.text
    assert deposit_proof.json()["deposit_status"] == "PENDING"

    confirm_deposit = client.patch(
        f"/admin/deposits/{buyer_id}",
        json={"status": "CONFIRMED", "reason": "tscheck deposit confirmed"},
        headers={"Cookie": finance["cookie_header"]},
    )
    assert confirm_deposit.status_code == 200, confirm_deposit.text
    assert confirm_deposit.json()["deposit_status"] == "CONFIRMED"

    # 6. Access status now fully eligible
    access_resp = client.get("/deposits/access", params={"bidder_name": full_name})
    assert access_resp.status_code == 200, access_resp.text
    access = access_resp.json()
    assert access["eligible"] is True, access
    assert access["reasons"] == []

    # 7. Bid now succeeds on a LIVE lot
    lot_resp = client.get("/lots/lot-001")
    assert lot_resp.status_code == 200
    lot = lot_resp.json()
    bid_amount = max(lot["base_price"], lot["current_bid"] + lot["minimum_increment"])
    final_bid = client.post("/lots/lot-001/bids", json={"bidder_name": full_name, "bidder_type": "individual", "amount": bid_amount})
    assert final_bid.status_code == 201, final_bid.text
    assert final_bid.json()["amount"] == bid_amount
