"""Bidding is anonymous (Bidder #...) and anti-sniping extends closing time by 30s when a
valid bid lands inside the final 30 seconds of the auction window.
"""

from datetime import datetime, timedelta

import httpx

LOT_ID = "lot-003"  # LIVE lot dedicated to this check to avoid clobbering other checks' lot-001 state
ELIGIBLE_BIDDER = "Budi Santoso"  # seeded fully-eligible buyer (MPI-001)


def test_bid_list_shows_anonymized_bidder_name(client: httpx.Client, login_as):
    admin = login_as(client, "superadmin", "MITAuction!2026")
    far_future = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    ensure_live = client.patch(f"/admin/lots/{LOT_ID}", json={"status": "LIVE", "auction_end": far_future}, headers={"Cookie": admin["cookie_header"]})
    assert ensure_live.status_code == 200, ensure_live.text

    lot = client.get(f"/lots/{LOT_ID}").json()
    bid_amount = max(lot["base_price"], lot["current_bid"] + lot["minimum_increment"])
    placed = client.post(f"/lots/{LOT_ID}/bids", json={"bidder_name": ELIGIBLE_BIDDER, "bidder_type": "individual", "amount": bid_amount})
    assert placed.status_code == 201, placed.text

    bids = client.get(f"/lots/{LOT_ID}/bids")
    assert bids.status_code == 200
    entries = bids.json()
    assert len(entries) > 0
    for entry in entries:
        assert entry["bidder_name"].startswith("Bidder #"), entry


def test_bid_in_final_30_seconds_extends_closing(client: httpx.Client, login_as):
    admin = login_as(client, "superadmin", "MITAuction!2026")
    now = datetime.utcnow()
    soon_close = now + timedelta(seconds=15)
    patch_resp = client.patch(
        f"/admin/lots/{LOT_ID}",
        json={"status": "LIVE", "auction_end": soon_close.isoformat()},
        headers={"Cookie": admin["cookie_header"]},
    )
    assert patch_resp.status_code == 200, patch_resp.text
    patched_lot = patch_resp.json()
    original_end = patched_lot["auction_end"]

    lot = client.get(f"/lots/{LOT_ID}").json()
    bid_amount = max(lot["base_price"], lot["current_bid"] + lot["minimum_increment"])
    placed = client.post(f"/lots/{LOT_ID}/bids", json={"bidder_name": ELIGIBLE_BIDDER, "bidder_type": "individual", "amount": bid_amount})
    assert placed.status_code == 201, placed.text

    updated_lot = client.get(f"/lots/{LOT_ID}").json()
    from datetime import datetime as dt

    delta = dt.fromisoformat(updated_lot["auction_end"]) - dt.fromisoformat(original_end)
    assert delta.total_seconds() >= 29, f"expected ~30s extension, got {delta.total_seconds()}s (before={original_end} after={updated_lot['auction_end']})"
