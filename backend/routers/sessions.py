from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pymongo import ASCENDING, ReturnDocument

from lib.admin_auth import require_super_admin
from lib.dates import default_auction_slots
from lib.db import db
from models.marketplace import AdminUserPublic
from models.operations import AuctionSession, AuctionSessionUpdate


router = APIRouter(prefix="/sessions", tags=["sessions"])
admin_router = APIRouter(prefix="/admin/sessions", tags=["admin-sessions"])


@router.get("", response_model=list[AuctionSession])
async def public_sessions():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    documents = await db.auction_sessions.find({"publication_at": {"$lte": now}, "status": {"$in": ["PUBLISHED", "LIVE", "CLOSED"]}}).sort("start_at", ASCENDING).to_list(30)
    return [AuctionSession(**document) for document in documents]


@router.get("/{session_id}", response_model=AuctionSession)
async def public_session(session_id: str):
    document = await db.auction_sessions.find_one({"id": session_id})
    if not document:
        raise HTTPException(status_code=404, detail="Sesi lelang tidak ditemukan")
    return AuctionSession(**document)


@admin_router.get("", response_model=list[AuctionSession])
async def admin_sessions(current: AdminUserPublic = Depends(require_super_admin)):
    documents = await db.auction_sessions.find().sort("start_at", ASCENDING).to_list(100)
    return [AuctionSession(**document) for document in documents]


@admin_router.post("/generate", response_model=list[AuctionSession])
async def generate_default_sessions(current: AdminUserPublic = Depends(require_super_admin)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for slot in default_auction_slots(6):
        code = f"MIT-{slot['local_date'].replace('-', '')}"
        await db.auction_sessions.update_one(
            {"code": code},
            {"$setOnInsert": {"id": str(__import__('uuid').uuid4()), "code": code, "title": f"Lelang Reguler {slot['local_date']}", "start_at": slot["start_at"], "end_at": slot["end_at"], "publication_at": slot["publication_at"], "status": slot["status"], "lot_ids": [], "created_at": now}},
            upsert=True,
        )
    documents = await db.auction_sessions.find().sort("start_at", ASCENDING).to_list(100)
    return [AuctionSession(**document) for document in documents]


@admin_router.patch("/{session_id}", response_model=AuctionSession)
async def update_session(session_id: str, input: AuctionSessionUpdate, current: AdminUserPublic = Depends(require_super_admin)):
    values = input.model_dump(exclude_none=True)
    document = await db.auction_sessions.find_one_and_update({"id": session_id}, {"$set": values}, return_document=ReturnDocument.AFTER)
    if not document:
        raise HTTPException(status_code=404, detail="Sesi lelang tidak ditemukan")
    return AuctionSession(**document)