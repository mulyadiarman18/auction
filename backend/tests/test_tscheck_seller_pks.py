"""Seller & PKS: the demo vendor (vendor-demo-001) exposes an ACTIVE PKS, contract, 1.5% fee
and pool/settlement data; a vendor without APPROVED legality + ACTIVE PKS is rejected when
submitting a unit for auction.
"""

import uuid

import httpx


def test_demo_vendor_shows_active_pks_contract_and_fee(client: httpx.Client):
    resp = client.get("/vendors/vendor-demo-001")
    assert resp.status_code == 200, resp.text
    vendor = resp.json()
    assert vendor["legality_status"] == "APPROVED", vendor
    assert vendor["pks_status"] == "ACTIVE", vendor
    assert vendor["admin_fee_percent"] == 1.5
    assert vendor["contract_number"]
    assert vendor["pool_address"]
    assert vendor["settlement_terms"]

    settlements = client.get("/vendors/vendor-demo-001/settlements")
    assert settlements.status_code == 200, settlements.text
    for item in settlements.json():
        assert item["admin_fee_percent"] == 1.5


def test_vendor_without_active_pks_rejected_on_unit_submit(client: httpx.Client):
    suffix = uuid.uuid4().hex[:10]
    register_resp = client.post(
        "/vendors/register",
        json={
            "company_name": f"tscheck-vendor-{suffix}",
            "tax_number": f"09.{suffix[:8]}",
            "address": "Samarinda, tscheck fixture",
            "pic_name": "Tester PIC",
            "email": f"tscheck-vendor-{suffix}@example.com",
            "phone": "081399900011",
        },
    )
    assert register_resp.status_code == 201, register_resp.text
    vendor = register_resp.json()
    assert vendor["legality_status"] == "INCOMPLETE"
    assert vendor["pks_status"] == "NOT_UPLOADED"

    unit_resp = client.post(
        f"/vendors/{vendor['id']}/units",
        json={
            "unit_name": f"tscheck-unit-{suffix}",
            "category": "Excavator",
            "brand": "Komatsu",
            "model_type": "PC200",
            "year": 2019,
            "unit_number": f"U-{suffix[:6]}",
            "hull_number": f"H-{suffix[:6]}",
            "operating_hours": "1000 HM",
            "pool_location": "Pool tscheck",
            "proposed_price": 500_000_000,
        },
    )
    assert unit_resp.status_code == 403, unit_resp.text
