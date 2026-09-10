"""Internal role separation: Finance cannot manage unit inventory, Reviewer cannot confirm
payments, Inspector cannot see Finance's deposit queue. Every cross-role access returns 403.
"""

import httpx


def test_finance_forbidden_from_lot_management(client: httpx.Client, login_as):
    finance = login_as(client, "finance", "MITFinance!2026")
    resp = client.get("/admin/lots", headers={"Cookie": finance["cookie_header"]})
    assert resp.status_code == 403, resp.text


def test_reviewer_forbidden_from_confirming_deposit(client: httpx.Client, login_as):
    reviewer = login_as(client, "reviewer", "MITReview!2026")
    resp = client.patch(
        "/admin/deposits/nonexistent-buyer-id",
        json={"status": "CONFIRMED", "reason": "tscheck should be forbidden"},
        headers={"Cookie": reviewer["cookie_header"]},
    )
    assert resp.status_code == 403, resp.text


def test_inspector_forbidden_from_finance_queues(client: httpx.Client, login_as):
    inspector = login_as(client, "inspector", "MITInspect!2026")
    resp = client.get("/admin/deposits", headers={"Cookie": inspector["cookie_header"]})
    assert resp.status_code == 403, resp.text
    resp2 = client.get("/admin/invoices", headers={"Cookie": inspector["cookie_header"]})
    assert resp2.status_code == 403, resp2.text


def test_finance_sees_own_domain_only(client: httpx.Client, login_as):
    finance = login_as(client, "finance", "MITFinance!2026")
    memberships = client.get("/admin/member-payments", headers={"Cookie": finance["cookie_header"]})
    deposits = client.get("/admin/deposits", headers={"Cookie": finance["cookie_header"]})
    invoices = client.get("/admin/invoices", headers={"Cookie": finance["cookie_header"]})
    assert memberships.status_code == 200, memberships.text
    assert deposits.status_code == 200, deposits.text
    assert invoices.status_code == 200, invoices.text


def test_inspector_sees_only_own_inspection_tasks(client: httpx.Client, login_as):
    inspector = login_as(client, "inspector", "MITInspect!2026")
    resp = client.get("/admin/inspections", headers={"Cookie": inspector["cookie_header"]})
    assert resp.status_code == 200, resp.text
    tasks = resp.json()
    assert len(tasks) > 0
    assert all(task["inspector_name"] == inspector["user"]["name"] for task in tasks)
