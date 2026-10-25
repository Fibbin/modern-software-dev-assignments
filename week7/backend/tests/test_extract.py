from backend.app.services.extract import extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items


def test_extract_complex_regex_patterns():
    text = """
    Meeting notes
    1. FIXME: handle timeout on save
    - [ ] draft the release notes
    - [x] already shipped login
    Need to deploy tonight
    @bob: review the design doc
    Follow up with legal due 2026-10-30
    Please ping the oncall before Friday
    Let's schedule a retro
    See the spec. TODO: add examples in the README
    TODO: write tests
    Random observation about the weather
    """.strip()
    items = extract_action_items(text)

    assert "FIXME: handle timeout on save" in items
    assert "draft the release notes" in items
    assert "Need to deploy tonight" in items
    assert "@bob: review the design doc" in items
    assert "Follow up with legal due 2026-10-30" in items
    assert "Please ping the oncall before Friday" in items
    assert "Let's schedule a retro" in items
    assert "TODO: add examples in the README" in items
    assert "TODO: write tests" in items

    assert "already shipped login" not in items
    assert "Random observation about the weather" not in items
    assert items.count("TODO: write tests") == 1
