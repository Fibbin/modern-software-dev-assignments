import os
import json
from unittest.mock import patch, MagicMock

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_with_bullets(mock_chat: MagicMock):
    text = """
    - Set up database
    - Implement API endpoint
    """.strip()

    mock_chat.return_value = {
        "message": {
            "content": json.dumps(
                {"items": ["Set up database", "Implement API endpoint"]}
            )
        }
    }

    items = extract_action_items_llm(text)

    assert items == ["Set up database", "Implement API endpoint"]


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_with_keyword_prefix(mock_chat: MagicMock):
    text = "TODO: finish report and send to team"

    mock_chat.return_value = {
        "message": {
            "content": json.dumps({"items": ["finish report and send to team"]})
        }
    }

    items = extract_action_items_llm(text)

    assert items == ["finish report and send to team"]


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_with_empty_input(mock_chat: MagicMock):
    text = ""

    mock_chat.return_value = {
        "message": {
            "content": json.dumps({"items": []})
        }
    }

    items = extract_action_items_llm(text)

    assert items == []


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_with_no_action_items(mock_chat: MagicMock):
    text = """
    Today we discussed the overall architecture of the system.
    The team shared their thoughts and feedback.
    No specific tasks were agreed upon.
    """.strip()

    mock_chat.return_value = {
        "message": {
            "content": json.dumps({"items": []})
        }
    }

    items = extract_action_items_llm(text)

    assert items == []
