from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db


router = APIRouter(prefix="/notes", tags=["notes"])


class NoteCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


@router.get("")
def list_notes(limit: int = 13) -> list[NoteResponse]:
    rows = db.list_notes(limit=limit)
    return [NoteResponse(id=r["id"], content=r["content"], created_at=r["created_at"]) for r in rows]


@router.post("")
def create_note(payload: NoteCreateRequest) -> NoteResponse:
    content = payload.content.strip()
    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    return NoteResponse(id=note["id"], content=note["content"], created_at=note["created_at"])


@router.get("/{note_id}")
def get_single_note(note_id: int) -> NoteResponse:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])


