import pytest
from backend.app.db import get_db
from backend.app.main import app
from backend.app.models import ActionItem
from sqlalchemy import select, text


def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_action_item_404_and_validation_errors(client):
    not_found = client.put("/action-items/999999/complete")
    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "Action item not found"

    bad_payload = client.post("/action-items/", json={})
    assert bad_payload.status_code in (400, 422)

    invalid_id = client.put("/action-items/not-an-int/complete")
    assert invalid_id.status_code in (400, 422)


def test_action_items_transactional_rollback_and_index(client):
    override_fn = app.dependency_overrides[get_db]

    db_gen = override_fn()
    session = next(db_gen)
    with pytest.raises(RuntimeError):
        session.add(ActionItem(description="Should be rolled back", completed=False))
        session.flush()
        raise RuntimeError("Simulated mid-transaction failure")
    try:
        db_gen.throw(RuntimeError("Simulated mid-transaction failure"))
    except RuntimeError:
        pass

    verify_gen = override_fn()
    verify_session = next(verify_gen)
    try:
        rows = (
            verify_session.execute(
                select(ActionItem).where(ActionItem.description == "Should be rolled back")
            )
            .scalars()
            .all()
        )
        assert len(rows) == 0

        idx_rows = verify_session.execute(text("PRAGMA index_list('action_items')")).fetchall()
        idx_names = [row[1] for row in idx_rows]
        assert "ix_action_items_completed" in idx_names
    finally:
        try:
            next(verify_gen)
        except StopIteration:
            pass


def test_bulk_sequential_operations_consistency(client):
    created_ids = []
    for i in range(25):
        resp = client.post("/action-items/", json={"description": f"Bulk task {i}"})
        assert resp.status_code == 201
        created_ids.append(resp.json()["id"])

    for item_id in created_ids[:10]:
        comp = client.put(f"/action-items/{item_id}/complete")
        assert comp.status_code == 200
        assert comp.json()["completed"] is True

    all_items = client.get("/action-items/").json()
    completed_count = sum(1 for item in all_items if item["completed"])
    assert len(all_items) == 25
    assert completed_count == 10
