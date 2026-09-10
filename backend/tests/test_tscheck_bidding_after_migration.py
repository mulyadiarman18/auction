"""Bidding tetap berfungsi setelah migrasi data — POST /api/lots/{lot_id}/bids.

Covers: quick bid on a LIVE mining lot (lot-001) updates the highest bid and
stores bid activity without error. Also checks that bidding on a non-LIVE lot
(lot-002, UPCOMING) is rejected.
"""

import httpx


def test_bid_on_live_mining_lot_updates_highest_bid(client: httpx.Client):
    lot_id = "lot-001"

    before = client.get(f"/lots/{lot_id}")
    assert before.status_code == 200, before.text
    lot_before = before.json()
    assert lot_before["status"] == "LIVE"
    current_bid = lot_before["current_bid"]
    increment = lot_before["minimum_increment"]
    new_amount = current_bid + increment

    # Bidding now requires full eligibility (APPROVED + membership ACTIVE + deposit
    # CONFIRMED) per the newer "Backend memblokir bidding tanpa eligibility lengkap"
    # criterion, so this uses the seeded eligible member instead of an arbitrary name.
    bidder_name = "Budi Santoso"
    resp = client.post(
        f"/lots/{lot_id}/bids",
        json={"amount": new_amount, "bidder_name": bidder_name, "bidder_type": "Verified Bidder VIP"},
    )
    assert resp.status_code in (200, 201), resp.text
    created = resp.json()
    assert created["amount"] == new_amount
    assert created["lot_id"] == lot_id
    assert created["bidder_name"] == bidder_name

    after = client.get(f"/lots/{lot_id}")
    assert after.status_code == 200, after.text
    lot_after = after.json()
    assert lot_after["current_bid"] == new_amount, "highest bid was not updated after a valid quick bid"

    bids_resp = client.get(f"/lots/{lot_id}/bids")
    assert bids_resp.status_code == 200, bids_resp.text
    bids = bids_resp.json()
    assert any(b["id"] == created["id"] and b["amount"] == new_amount for b in bids), (
        "newly placed bid was not persisted in bid activity"
    )


def test_bid_rejected_on_non_live_lot(client: httpx.Client):
    lot_id = "lot-002"  # UPCOMING per seed facts

    before = client.get(f"/lots/{lot_id}")
    assert before.status_code == 200, before.text
    lot_before = before.json()
    assert lot_before["status"] != "LIVE"
    new_amount = lot_before["current_bid"] + lot_before["minimum_increment"]

    resp = client.post(
        f"/lots/{lot_id}/bids",
        json={"amount": new_amount, "bidder_name": "Budi Santoso", "bidder_type": "Verified Bidder VIP"},
    )
    assert resp.status_code >= 400, (
        f"expected rejection for bidding on non-LIVE lot {lot_id}, got {resp.status_code}: {resp.text}"
    )
