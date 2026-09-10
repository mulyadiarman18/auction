"""Inspection & grading: Inspector sees only own tasks, uploads a slot photo, scores at
least five component groups, and the system computes an A-D grade and updates the lot.
"""

import io

import httpx


def test_inspector_completes_grading_and_lot_is_updated(client: httpx.Client, login_as):
    inspector = login_as(client, "inspector", "MITInspect!2026")

    tasks_resp = client.get("/admin/inspections", headers={"Cookie": inspector["cookie_header"]})
    assert tasks_resp.status_code == 200, tasks_resp.text
    tasks = tasks_resp.json()
    assert len(tasks) > 0, "expected at least one inspection task assigned to the inspector fixture"
    target = tasks[0]
    assert target["inspector_name"] == inspector["user"]["name"]

    photo_resp = client.post(
        f"/admin/inspections/{target['id']}/photos/front",
        files={"file": ("front.png", io.BytesIO(b"fake-photo-bytes"), "image/png")},
        headers={"Cookie": inspector["cookie_header"]},
    )
    assert photo_resp.status_code == 200, photo_resp.text
    assert any(p["slot"] == "front" for p in photo_resp.json()["photos"])

    scores = {"eksterior": 90, "interior": 88, "mesin": 92, "kaki_kaki": 85, "kelistrikan": 91}
    submit_resp = client.patch(
        f"/admin/inspections/{target['id']}",
        json={"component_scores": scores, "notes": "tscheck grading run"},
        headers={"Cookie": inspector["cookie_header"]},
    )
    assert submit_resp.status_code == 200, submit_resp.text
    record = submit_resp.json()
    assert record["status"] == "COMPLETED"
    assert record["suggested_grade"] in ("A", "B", "C", "D")
    expected_total = round(sum(scores.values()) / len(scores))
    assert record["total_score"] == expected_total

    lot_resp = client.get(f"/lots/{target['lot_id']}")
    assert lot_resp.status_code == 200
    lot = lot_resp.json()
    assert lot["inspection_status"] == "COMPLETED"
    assert lot["inspection_score"] == expected_total
    assert lot["grade"] == f"Grade {record['suggested_grade']}"


def test_inspector_cannot_score_fewer_than_five_groups(client: httpx.Client, login_as):
    inspector = login_as(client, "inspector", "MITInspect!2026")
    tasks = client.get("/admin/inspections", headers={"Cookie": inspector["cookie_header"]}).json()
    assert len(tasks) > 0
    target = tasks[0]
    resp = client.patch(
        f"/admin/inspections/{target['id']}",
        json={"component_scores": {"eksterior": 80, "interior": 80}, "notes": "too few groups"},
        headers={"Cookie": inspector["cookie_header"]},
    )
    assert resp.status_code == 400, resp.text
