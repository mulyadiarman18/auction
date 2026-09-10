"""Winner invoice = hammer price minus the Rp3.000.000 deposit; member uploads proof of
final payment and Finance flips the invoice to PAID.
"""

import io

import httpx


def test_invoice_deducts_deposit_and_finance_marks_paid(client: httpx.Client, login_as):
    finance = login_as(client, "finance", "MITFinance!2026")

    lot = client.get("/lots/lot-001").json()
    buyer = client.get("/buyers/status/by-name", params={"full_name": "Budi Santoso"}).json()["profile"]

    seed_resp = client.post(
        f"/admin/invoices/seed-winner/lot-001",
        params={"buyer_id": buyer["id"]},
        headers={"Cookie": finance["cookie_header"]},
    )
    assert seed_resp.status_code == 200, seed_resp.text
    invoice = seed_resp.json()
    assert invoice["hammer_price"] == lot["current_bid"]
    assert invoice["deposit_deduction"] == buyer["deposit_amount"]
    assert invoice["total_due"] == lot["current_bid"] - buyer["deposit_amount"]
    assert invoice["status"] == "PENDING_PAYMENT"

    proof_resp = client.post(
        f"/transactions/{invoice['id']}/proof",
        files={"file": ("lunas.png", io.BytesIO(b"fake-payment-proof"), "image/png")},
    )
    assert proof_resp.status_code == 200, proof_resp.text
    assert proof_resp.json()["status"] == "PAYMENT_REVIEW"

    confirm_resp = client.patch(
        f"/admin/invoices/{invoice['id']}",
        json={"status": "CONFIRMED", "reason": "tscheck pelunasan diverifikasi"},
        headers={"Cookie": finance["cookie_header"]},
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    assert confirm_resp.json()["status"] == "PAID"

    member_invoices = client.get("/transactions", params={"bidder_name": "Budi Santoso"})
    assert member_invoices.status_code == 200, member_invoices.text
    assert any(item["id"] == invoice["id"] and item["status"] == "PAID" for item in member_invoices.json())
