from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


class ActionItemsExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    save_note: bool = False


class ExtractedActionItem(BaseModel):
    id: int
    text: str


class ActionItemsExtractResponse(BaseModel):
    note_id: Optional[int]
    items: List[ExtractedActionItem]


class ActionItem(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


class MarkDoneRequest(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool


@router.post("/extract")
def extract(payload: ActionItemsExtractRequest) -> ActionItemsExtractResponse:
    text = payload.text.strip()
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ActionItemsExtractResponse(
        note_id=note_id,
        items=[ExtractedActionItem(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.post("/extract-llm")
def extract_llm(payload: ActionItemsExtractRequest) -> ActionItemsExtractResponse:
    text = payload.text.strip()
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items_llm(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ActionItemsExtractResponse(
        note_id=note_id,
        items=[ExtractedActionItem(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.get("")
def list_all(note_id: Optional[int] = None) -> List[ActionItem]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItem(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    updated = db.mark_action_item_done(action_item_id, payload.done)
    if not updated:
        raise HTTPException(status_code=404, detail="action item not found")
    return MarkDoneResponse(id=action_item_id, done=payload.done)


