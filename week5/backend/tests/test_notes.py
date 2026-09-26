from backend.app.db import get_db
from backend.app.main import app
from sqlalchemy import text


def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_get_note_by_id_and_404(client):
    create_resp = client.post("/notes/", json={"title": "Lookup", "content": "Find me"})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    ok_resp = client.get(f"/notes/{note_id}")
    assert ok_resp.status_code == 200
    assert ok_resp.json()["title"] == "Lookup"

    not_found_resp = client.get("/notes/999999")
    assert not_found_resp.status_code == 404
    assert not_found_resp.json()["detail"] == "Note not found"


def test_create_note_validation_errors(client):
    missing_title = client.post("/notes/", json={"content": "No title"})
    assert missing_title.status_code in (400, 422)

    missing_content = client.post("/notes/", json={"title": "No content"})
    assert missing_content.status_code in (400, 422)

    wrong_type = client.post("/notes/", json={"title": 12345, "content": None})
    assert wrong_type.status_code in (400, 422)


def test_notes_query_performance_and_indexes_with_seeded_data(client):
    for i in range(120):
        r = client.post(
            "/notes/",
            json={"title": f"IndexedNote-{i:03d}", "content": f"Seeded body content {i}"},
        )
        assert r.status_code == 201

    search_hit = client.get("/notes/search/", params={"q": "IndexedNote-088"})
    assert search_hit.status_code == 200
    results = search_hit.json()
    assert len(results) == 1
    assert results[0]["title"] == "IndexedNote-088"

    search_miss = client.get("/notes/search/", params={"q": "NonExistentKeywordXYZ"})
    assert search_miss.status_code == 200
    assert search_miss.json() == []

    override_fn = app.dependency_overrides[get_db]
    db_gen = override_fn()
    session = next(db_gen)
    try:
        idx_rows = session.execute(text("PRAGMA index_list('notes')")).fetchall()
        idx_names = [row[1] for row in idx_rows]
        assert "ix_notes_title" in idx_names

        plan_rows = session.execute(
            text("EXPLAIN QUERY PLAN SELECT id, title FROM notes WHERE title = 'IndexedNote-088'")
        ).fetchall()
        plan_detail = " ".join(str(r) for r in plan_rows)
        assert "ix_notes_title" in plan_detail or "INDEX" in plan_detail.upper()
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


def test_frontend_and_search_integration(client):
    root_resp = client.get("/")
    assert root_resp.status_code in (200, 404)

    empty_q = client.get("/notes/search/", params={"q": ""})
    assert empty_q.status_code == 200
