"""Criterion: Role permissions membedakan Super Admin dan Reviewer.

Backend must reject PATCH /admin/lots/{id} with admin_role=reviewer (403),
and accept it for admin_role=super_admin.
"""


def test_reviewer_cannot_patch_lot(client):
    lots = client.get("/admin/lots", params={"admin_role": "super_admin"})
    assert lots.status_code == 200
    body = lots.json()
    assert len(body) > 0
    lot_id = body[0]["id"]

    resp = client.patch(f"/admin/lots/{lot_id}", params={"admin_role": "reviewer"}, json={"status": "LIVE"})
    assert resp.status_code == 403, resp.text
    assert "Super Admin" in resp.json()["detail"]


def test_super_admin_can_patch_lot(client):
    lots = client.get("/admin/lots", params={"admin_role": "super_admin"})
    assert lots.status_code == 200
    lot = lots.json()[0]
    lot_id = lot["id"]
    original_status = lot["status"]

    resp = client.patch(f"/admin/lots/{lot_id}", params={"admin_role": "super_admin"}, json={"status": original_status})
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == lot_id
