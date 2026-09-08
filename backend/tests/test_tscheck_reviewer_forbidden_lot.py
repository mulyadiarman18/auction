"""Criterion: Reviewer hanya dapat review peserta.

Reviewer session must be rejected (403) from mutating/listing /admin/lots,
while a Super Admin session on the same lot succeeds.
"""

def test_reviewer_forbidden_from_lot_mutation_but_superadmin_allowed(client, login_as):
    sa_session = login_as(client, "superadmin", "MITAuction!2026")
    sa_headers = {"Cookie": sa_session["cookie_header"]}
    lots = client.get("/admin/lots", headers=sa_headers)
    assert lots.status_code == 200, lots.text
    lot = lots.json()[0]
    lot_id = lot["id"]
    original_status = lot["status"]

    rv_session = login_as(client, "reviewer", "MITReview!2026")
    rv_headers = {"Cookie": rv_session["cookie_header"]}

    forbidden = client.patch(f"/admin/lots/{lot_id}", json={"status": original_status}, headers=rv_headers)
    assert forbidden.status_code == 403, forbidden.text

    forbidden_list = client.get("/admin/lots", headers=rv_headers)
    assert forbidden_list.status_code == 403, forbidden_list.text

    allowed = client.patch(f"/admin/lots/{lot_id}", json={"status": original_status}, headers=sa_headers)
    assert allowed.status_code == 200, allowed.text
    assert allowed.json()["id"] == lot_id
