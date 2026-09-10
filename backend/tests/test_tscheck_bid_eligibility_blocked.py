"""Criterion: Backend memblokir bidding tanpa eligibility lengkap.

POST /lots/{lot_id}/bids must reject (403) bidders that are not
APPROVED + membership ACTIVE + deposit CONFIRMED, and must accept (201) a
bidder that satisfies all three (seeded member Budi Santoso).
"""

import time

import httpx


LIVE_LOT_ID = "lot-001"


def _register_incomplete_buyer(client: httpx.Client) -> str:
    unique = f"tscheck-bid-elig-{int(time.time() * 1000)}"
    payload = {
        "buyer_type": "individual",
        "full_name": unique,
        "email": f"{unique}@example.com",
        "phone": "081200000099",
        "identity_number": "3170000000009999",
        "company_name": "",
        "tax_number": "",
        "address": "Jakarta",
    }
    resp = client.post("/buyers/register", json=payload)
    assert resp.status_code == 201, resp.text
    return unique


def test_bid_rejected_for_ineligible_bidder(client: httpx.Client):
    bidder_name = _register_incomplete_buyer(client)

    resp = client.post(
        f"/lots/{LIVE_LOT_ID}/bids",
        json={"bidder_name": bidder_name, "bidder_type": "individual", "amount": 999_999_999_999},
    )

    assert resp.status_code == 403, resp.text
    assert "APPROVED" in resp.text or "eligibility" in resp.text.lower() or "membership" in resp.text.lower() or "deposit" in resp.text.lower() or "membutuhkan" in resp.text.lower()


def test_bid_accepted_for_eligible_seeded_member(client: httpx.Client):
    lot_resp = client.get(f"/lots/{LIVE_LOT_ID}")
    assert lot_resp.status_code == 200, lot_resp.text
    lot = lot_resp.json()
    minimum_amount = max(lot["base_price"], lot["current_bid"] + lot["minimum_increment"])

    resp = client.post(
        f"/lots/{LIVE_LOT_ID}/bids",
        json={"bidder_name": "Budi Santoso", "bidder_type": "individual", "amount": minimum_amount},
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["bidder_name"] == "Budi Santoso"
    assert body["amount"] == minimum_amount
    assert body["lot_id"] == LIVE_LOT_ID

    # Confirm it is reflected on the lot.
    updated_lot = client.get(f"/lots/{LIVE_LOT_ID}").json()
    assert updated_lot["current_bid"] == minimum_amount
