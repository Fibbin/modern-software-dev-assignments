import pytest


def _create_notes(client, titles: list[str]) -> list[dict]:
    notes = []
    for title in titles:
        r = client.post("/notes/", json={"title": title, "content": f"body for {title}"})
        assert r.status_code == 201, r.text
        notes.append(r.json())
    return notes


def _create_actions(client, descriptions: list[str]) -> list[dict]:
    items = []
    for description in descriptions:
        r = client.post("/action-items/", json={"description": description})
        assert r.status_code == 201, r.text
        items.append(r.json())
    return items


def test_notes_pagination_pages_and_remainder(client):
    titles = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]
    created = _create_notes(client, titles)

    first = client.get("/notes/", params={"skip": 0, "limit": 2, "sort": "id"})
    assert first.status_code == 200
    assert [n["title"] for n in first.json()] == ["Alpha", "Bravo"]

    second = client.get("/notes/", params={"skip": 2, "limit": 2, "sort": "id"})
    assert second.status_code == 200
    assert [n["title"] for n in second.json()] == ["Charlie", "Delta"]

    last = client.get("/notes/", params={"skip": 4, "limit": 2, "sort": "id"})
    assert last.status_code == 200
    assert [n["title"] for n in last.json()] == ["Echo"]

    past_end = client.get("/notes/", params={"skip": len(created), "limit": 2, "sort": "id"})
    assert past_end.status_code == 200
    assert past_end.json() == []


def test_notes_sort_title_asc_and_desc(client):
    _create_notes(client, ["Charlie", "Alpha", "Bravo"])

    asc_res = client.get("/notes/", params={"sort": "title"})
    assert asc_res.status_code == 200
    assert [n["title"] for n in asc_res.json()] == ["Alpha", "Bravo", "Charlie"]

    desc_res = client.get("/notes/", params={"sort": "-title"})
    assert desc_res.status_code == 200
    assert [n["title"] for n in desc_res.json()] == ["Charlie", "Bravo", "Alpha"]


def test_notes_default_sort_is_newest_first(client):
    created = _create_notes(client, ["First", "Second", "Third"])
    newest_first = list(reversed(created))

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert [n["id"] for n in items] == [n["id"] for n in newest_first]
    assert items[0]["title"] == "Third"


def test_notes_invalid_sort_falls_back_to_created_at_desc(client):
    created = _create_notes(client, ["One", "Two", "Three"])

    r = client.get("/notes/", params={"sort": "not_a_column"})
    assert r.status_code == 200
    assert [n["id"] for n in r.json()] == list(reversed([n["id"] for n in created]))


def test_notes_search_combined_with_sort_and_limit(client):
    _create_notes(client, ["Apple pie", "Banana", "Green apple", "Cherry"])

    r = client.get("/notes/", params={"q": "apple", "sort": "title", "limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Apple pie"

    r = client.get("/notes/", params={"q": "apple", "sort": "title", "skip": 1, "limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Green apple"


@pytest.mark.parametrize(
    ("params", "status"),
    [
        ({"skip": -1}, 422),
        ({"limit": 0}, 422),
        ({"limit": 201}, 422),
    ],
)
def test_notes_pagination_query_validation(client, params, status):
    r = client.get("/notes/", params=params)
    assert r.status_code == status


def test_action_items_pagination_and_description_sort(client):
    _create_actions(client, ["Write tests", "Review PR", "Ship it"])

    r = client.get("/action-items/", params={"sort": "description"})
    assert r.status_code == 200
    assert [i["description"] for i in r.json()] == ["Review PR", "Ship it", "Write tests"]

    page = client.get("/action-items/", params={"sort": "description", "skip": 1, "limit": 1})
    assert page.status_code == 200
    assert [i["description"] for i in page.json()] == ["Ship it"]


def test_action_items_pagination_with_completed_filter(client):
    created = _create_actions(client, ["Open A", "Open B", "Done C", "Open D", "Done E"])
    for item in created:
        if item["description"].startswith("Done"):
            r = client.put(f"/action-items/{item['id']}/complete")
            assert r.status_code == 200

    open_page = client.get(
        "/action-items/",
        params={"completed": False, "sort": "description", "skip": 0, "limit": 2},
    )
    assert open_page.status_code == 200
    assert [i["description"] for i in open_page.json()] == ["Open A", "Open B"]
    assert all(i["completed"] is False for i in open_page.json())

    open_rest = client.get(
        "/action-items/",
        params={"completed": False, "sort": "description", "skip": 2, "limit": 2},
    )
    assert open_rest.status_code == 200
    assert [i["description"] for i in open_rest.json()] == ["Open D"]

    done = client.get("/action-items/", params={"completed": True, "sort": "description"})
    assert done.status_code == 200
    assert [i["description"] for i in done.json()] == ["Done C", "Done E"]
    assert all(i["completed"] is True for i in done.json())


def test_action_items_invalid_sort_and_query_bounds(client):
    created = _create_actions(client, ["First", "Second"])

    r = client.get("/action-items/", params={"sort": "nope"})
    assert r.status_code == 200
    assert [i["id"] for i in r.json()] == list(reversed([i["id"] for i in created]))

    assert client.get("/action-items/", params={"skip": -5}).status_code == 422
    assert client.get("/action-items/", params={"limit": 0}).status_code == 422
    assert client.get("/action-items/", params={"limit": 201}).status_code == 422
