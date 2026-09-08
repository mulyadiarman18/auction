from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from lib.db import db
from lib.admin_auth import get_current_admin, require_super_admin
from models.auction import Lot
from models.marketplace import AdminAuditLog, AdminLotUpdate, AdminSummary, AdminUserPublic, AdminWinner, BuyerProfile, BuyerVerificationUpdate


router = APIRouter(prefix="/admin", tags=["admin"])
documents_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="buyer_documents")


@router.get("/summary", response_model=AdminSummary)
async def admin_summary(current: AdminUserPublic = Depends(get_current_admin)):
    total_lots = await db.lots.count_documents({})
    live_lots = await db.lots.count_documents({"status": "LIVE"})
    upcoming_lots = await db.lots.count_documents({"status": "UPCOMING"})
    ended_lots = await db.lots.count_documents({"status": "ENDED"})
    bids = await db.bids.find({}, {"amount": 1}).to_list(10000)
    pending_buyers = await db.buyers.count_documents({"verification_status": "PENDING"})
    return AdminSummary(total_lots=total_lots, live_lots=live_lots, upcoming_lots=upcoming_lots, ended_lots=ended_lots, total_bids=len(bids), total_bid_value=sum(int(bid.get("amount", 0)) for bid in bids), pending_buyers=pending_buyers)


@router.get("/lots", response_model=list[Lot])
async def admin_lots(current: AdminUserPublic = Depends(require_super_admin)):
    documents = await db.lots.find().sort([("status", ASCENDING), ("auction_end", ASCENDING)]).to_list(100)
    return [Lot(**document) for document in documents]


@router.patch("/lots/{lot_id}", response_model=Lot)
async def update_admin_lot(lot_id: str, input: AdminLotUpdate, current: AdminUserPublic = Depends(require_super_admin)):
    values = input.model_dump(exclude_none=True)
    if not values:
        raise HTTPException(status_code=400, detail="Tidak ada perubahan untuk disimpan")
    document = await db.lots.find_one_and_update({"id": lot_id}, {"$set": values}, return_document=True)
    if not document:
        raise HTTPException(status_code=404, detail="Lot tidak ditemukan")
    return Lot(**document)


@router.get("/winners", response_model=list[AdminWinner])
async def admin_winners(current: AdminUserPublic = Depends(require_super_admin)):
    lots = await db.lots.find().sort("auction_end", DESCENDING).to_list(100)
    winners: list[AdminWinner] = []
    for lot in lots:
        highest_bid = await db.bids.find_one({"lot_id": lot["id"]}, sort=[("amount", DESCENDING)])
        winner_status = "PENDING"
        if lot["status"] == "ENDED":
            winner_status = "WON" if highest_bid else "UNSOLD"
        winners.append(AdminWinner(lot_id=lot["id"], lot_number=lot["lot_number"], title=lot["title"], status=winner_status, bidder_name=highest_bid.get("bidder_name") if highest_bid and winner_status == "WON" else None, winning_bid=highest_bid.get("amount") if highest_bid and winner_status == "WON" else None, auction_end=lot["auction_end"]))
    return winners


@router.get("/buyers", response_model=list[BuyerProfile])
async def admin_buyers(status: str = "PENDING", current: AdminUserPublic = Depends(get_current_admin)):
    query = {"verification_status": status.upper(), "screening_status": "READY"} if status != "all" else {}
    documents = await db.buyers.find(query).sort("created_at", DESCENDING).to_list(100)
    return [BuyerProfile(**document) for document in documents]


@router.patch("/buyers/{buyer_id}", response_model=BuyerProfile)
async def update_buyer_verification(buyer_id: str, input: BuyerVerificationUpdate, current: AdminUserPublic = Depends(get_current_admin)):
    buyer = await db.buyers.find_one({"id": buyer_id})
    if not buyer:
        raise HTTPException(status_code=404, detail="Data peserta tidak ditemukan")
    if buyer.get("verification_status") != "PENDING":
        raise HTTPException(status_code=400, detail="Peserta ini sudah diproses sebelumnya")
    if buyer.get("screening_status") != "READY":
        raise HTTPException(status_code=400, detail="Peserta belum lolos auto screening")
    now = datetime.now(timezone.utc)
    document = await db.buyers.find_one_and_update(
        {"id": buyer_id, "verification_status": "PENDING"},
        {"$set": {"verification_status": input.verification_status, "reviewed_at": now, "reviewed_by": current.name, "review_reason": input.reason.strip() or "Data terverifikasi", "resubmission_required": input.verification_status == "REJECTED"}},
        return_document=ReturnDocument.AFTER,
    )
    if not document:
        raise HTTPException(status_code=409, detail="Status peserta baru saja berubah")
    audit = AdminAuditLog(
        entity_id=buyer_id,
        entity_name=document["full_name"],
        action="APPROVE" if input.verification_status == "APPROVED" else "REJECT",
        admin_name=current.name,
        admin_role=current.role,
        old_status="PENDING",
        new_status=input.verification_status,
        reason=input.reason.strip() or "Data terverifikasi",
        created_at=now,
    )
    await db.admin_audit_logs.insert_one(audit.model_dump())
    return BuyerProfile(**document)


@router.get("/audit-logs", response_model=list[AdminAuditLog])
async def admin_audit_logs(current: AdminUserPublic = Depends(get_current_admin)):
    documents = await db.admin_audit_logs.find().sort("created_at", DESCENDING).to_list(200)
    return [AdminAuditLog(**document) for document in documents]


@router.get("/buyers/{buyer_id}/documents/{document_id}")
async def download_buyer_document(buyer_id: str, document_id: str, current: AdminUserPublic = Depends(get_current_admin)):
    buyer = await db.buyers.find_one({"id": buyer_id})
    if not buyer:
        raise HTTPException(status_code=404, detail="Data peserta tidak ditemukan")
    metadata = next((item for item in buyer.get("documents", []) if item.get("id") == document_id), None)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    try:
        stream = await documents_bucket.open_download_stream(ObjectId(metadata["storage_id"]))
        contents = await stream.read()
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Berkas dokumen tidak tersedia") from exc
    safe_name = metadata["file_name"].replace('"', "")
    return Response(content=contents, media_type=metadata["content_type"], headers={"Content-Disposition": f'inline; filename="{safe_name}"'})