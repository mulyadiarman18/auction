from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import ASCENDING, ReturnDocument

from lib.admin_auth import require_finance
from lib.db import db
from models.marketplace import AdminUserPublic, BuyerProfile, DepositDocument
from models.operations import BidAccessStatus, DepositReviewItem, DepositReviewUpdate


router = APIRouter(prefix="/deposits", tags=["deposits"])
admin_router = APIRouter(prefix="/admin/deposits", tags=["admin-deposits"])
membership_router = APIRouter(prefix="/membership", tags=["membership"])
admin_membership_router = APIRouter(prefix="/admin/member-payments", tags=["admin-member-payments"])
bucket = AsyncIOMotorGridFSBucket(db, bucket_name="deposit_documents")
membership_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="membership_documents")
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_SIZE = 5 * 1024 * 1024


def access_from_buyer(name: str, buyer: dict | None) -> BidAccessStatus:
    if not buyer:
        return BidAccessStatus(bidder_name=name, reasons=["Registrasi member belum ditemukan"])
    reasons: list[str] = []
    if buyer.get("verification_status") != "APPROVED": reasons.append("Verifikasi bidder belum APPROVED")
    if buyer.get("membership_payment_status") != "CONFIRMED" or buyer.get("membership_status") != "ACTIVE": reasons.append("Biaya member Rp2.000.000 belum terkonfirmasi")
    if buyer.get("deposit_status") != "CONFIRMED": reasons.append("Deposit Rp3.000.000 belum terkonfirmasi")
    return BidAccessStatus(bidder_name=name, buyer_id=buyer["id"], verification_status=buyer.get("verification_status", "INCOMPLETE"), membership_status=buyer.get("membership_status", "INACTIVE"), deposit_status=buyer.get("deposit_status", "NOT_SUBMITTED"), deposit_amount=buyer.get("deposit_amount", 3_000_000), eligible=not reasons, reasons=reasons)


@router.get("/access", response_model=BidAccessStatus)
async def bidder_access(bidder_name: str = Query(min_length=2, max_length=100)):
    buyer = await db.buyers.find_one({"full_name": bidder_name}, sort=[("created_at", -1)])
    return access_from_buyer(bidder_name, buyer)


@router.post("/buyers/{buyer_id}/proof", response_model=BuyerProfile)
async def upload_deposit_proof(buyer_id: str, file: UploadFile = File(...)):
    buyer = await db.buyers.find_one({"id": buyer_id})
    if not buyer:
        raise HTTPException(status_code=404, detail="Data member tidak ditemukan")
    if buyer.get("verification_status") != "APPROVED" or buyer.get("membership_status") != "ACTIVE":
        raise HTTPException(status_code=400, detail="Member harus APPROVED dan aktif sebelum mengirim deposit")
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Bukti transfer harus PDF, JPG, atau PNG")
    contents = await file.read(MAX_SIZE + 1)
    if not contents or len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran bukti transfer maksimal 5 MB")
    storage_id = await bucket.upload_from_stream(file.filename or "deposit-proof", contents, metadata={"buyer_id": buyer_id, "content_type": content_type})
    document = DepositDocument(file_name=file.filename or "deposit-proof", content_type=content_type, size_bytes=len(contents), storage_id=str(storage_id), uploaded_at=datetime.now(timezone.utc))
    updated = await db.buyers.find_one_and_update({"id": buyer_id}, {"$set": {"deposit_status": "PENDING", "deposit_document": document.model_dump(), "deposit_reviewed_at": None, "deposit_reviewed_by": None, "deposit_review_reason": None}}, return_document=ReturnDocument.AFTER)
    return BuyerProfile(**updated)


@admin_router.get("", response_model=list[DepositReviewItem])
async def pending_deposits(current: AdminUserPublic = Depends(require_finance)):
    buyers = await db.buyers.find({"deposit_status": "PENDING", "deposit_document": {"$ne": None}}).sort("deposit_document.uploaded_at", ASCENDING).to_list(100)
    return [DepositReviewItem(buyer_id=buyer["id"], bidder_name=buyer["full_name"], email=buyer["email"], amount=buyer.get("deposit_amount", 3_000_000), status=buyer["deposit_status"], document_file_name=buyer["deposit_document"]["file_name"], submitted_at=buyer["deposit_document"]["uploaded_at"]) for buyer in buyers]


@admin_router.patch("/{buyer_id}", response_model=BuyerProfile)
async def review_deposit(buyer_id: str, input: DepositReviewUpdate, current: AdminUserPublic = Depends(require_finance)):
    buyer = await db.buyers.find_one({"id": buyer_id, "deposit_status": "PENDING"})
    if not buyer:
        raise HTTPException(status_code=404, detail="Deposit pending tidak ditemukan")
    if input.status == "REJECTED" and len(input.reason.strip()) < 5:
        raise HTTPException(status_code=400, detail="Alasan penolakan minimal 5 karakter")
    updated = await db.buyers.find_one_and_update({"id": buyer_id, "deposit_status": "PENDING"}, {"$set": {"deposit_status": input.status, "deposit_reviewed_at": datetime.now(timezone.utc), "deposit_reviewed_by": current.name, "deposit_review_reason": input.reason.strip() or "Bukti transfer terverifikasi"}}, return_document=ReturnDocument.AFTER)
    return BuyerProfile(**updated)


@admin_router.get("/{buyer_id}/proof")
async def preview_deposit_proof(buyer_id: str, current: AdminUserPublic = Depends(require_finance)):
    buyer = await db.buyers.find_one({"id": buyer_id})
    metadata = buyer.get("deposit_document") if buyer else None
    if not metadata:
        raise HTTPException(status_code=404, detail="Bukti deposit tidak ditemukan")
    stream = await bucket.open_download_stream(ObjectId(metadata["storage_id"]))
    contents = await stream.read()
    return Response(content=contents, media_type=metadata["content_type"], headers={"Content-Disposition": f'inline; filename="{metadata["file_name"].replace(chr(34), "")}"'})


@membership_router.post("/buyers/{buyer_id}/proof", response_model=BuyerProfile)
async def upload_membership_proof(buyer_id: str, file: UploadFile = File(...)):
    buyer = await db.buyers.find_one({"id": buyer_id})
    if not buyer or buyer.get("verification_status") != "APPROVED":
        raise HTTPException(status_code=400, detail="Bidder harus APPROVED sebelum membayar membership")
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Bukti pembayaran harus PDF, JPG, atau PNG")
    contents = await file.read(MAX_SIZE + 1)
    if not contents or len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran bukti maksimal 5 MB")
    storage_id = await membership_bucket.upload_from_stream(file.filename or "membership-proof", contents, metadata={"buyer_id": buyer_id, "content_type": content_type})
    document = DepositDocument(file_name=file.filename or "membership-proof", content_type=content_type, size_bytes=len(contents), storage_id=str(storage_id), uploaded_at=datetime.now(timezone.utc))
    updated = await db.buyers.find_one_and_update({"id": buyer_id}, {"$set": {"membership_payment_status": "PENDING", "membership_document": document.model_dump(), "membership_status": "INACTIVE"}}, return_document=ReturnDocument.AFTER)
    return BuyerProfile(**updated)


@admin_membership_router.get("", response_model=list[DepositReviewItem])
async def pending_memberships(current: AdminUserPublic = Depends(require_finance)):
    buyers = await db.buyers.find({"membership_payment_status": "PENDING", "membership_document": {"$ne": None}}).sort("membership_document.uploaded_at", ASCENDING).to_list(100)
    return [DepositReviewItem(buyer_id=buyer["id"], bidder_name=buyer["full_name"], email=buyer["email"], amount=buyer.get("membership_fee", 2_000_000), status=buyer["membership_payment_status"], document_file_name=buyer["membership_document"]["file_name"], submitted_at=buyer["membership_document"]["uploaded_at"]) for buyer in buyers]


@admin_membership_router.patch("/{buyer_id}", response_model=BuyerProfile)
async def review_membership(buyer_id: str, input: DepositReviewUpdate, current: AdminUserPublic = Depends(require_finance)):
    buyer = await db.buyers.find_one({"id": buyer_id, "membership_payment_status": "PENDING"})
    if not buyer:
        raise HTTPException(status_code=404, detail="Pembayaran membership pending tidak ditemukan")
    if input.status == "REJECTED" and len(input.reason.strip()) < 5:
        raise HTTPException(status_code=400, detail="Alasan penolakan minimal 5 karakter")
    values = {"membership_payment_status": input.status, "membership_status": "ACTIVE" if input.status == "CONFIRMED" else "INACTIVE", "deposit_reviewed_at": datetime.now(timezone.utc), "deposit_reviewed_by": current.name, "deposit_review_reason": input.reason.strip() or "Biaya member terverifikasi"}
    if input.status == "CONFIRMED":
        from datetime import timedelta
        values["membership_expires_at"] = datetime.now(timezone.utc) + timedelta(days=365)
    updated = await db.buyers.find_one_and_update({"id": buyer_id}, {"$set": values}, return_document=ReturnDocument.AFTER)
    return BuyerProfile(**updated)