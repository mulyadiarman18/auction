from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, Query, Response, UploadFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import DESCENDING

from lib.db import db
from models.marketplace import (
    BuyerProfile,
    BuyerRegistrationCreate,
    BuyerResubmissionUpdate,
    BuyerDocument,
    BuyerStatusResponse,
    WishlistItem,
    WishlistToggleRequest,
    WishlistToggleResponse,
)


buyers_router = APIRouter(prefix="/buyers", tags=["buyers"])
wishlist_router = APIRouter(prefix="/wishlists", tags=["wishlists"])
documents_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="buyer_documents")
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024


def screen_buyer(document: dict) -> tuple[str, list[str]]:
    issues: list[str] = []
    for field, label in (("full_name", "Nama lengkap"), ("email", "Email"), ("phone", "Nomor HP"), ("identity_number", "Nomor identitas"), ("address", "Alamat")):
        if not str(document.get(field, "")).strip():
            issues.append(f"{label} belum lengkap")
    document_types = {item.get("document_type") for item in document.get("documents", [])}
    if "identity_document" not in document_types:
        issues.append("Dokumen identitas belum diunggah")
    if document.get("buyer_type") == "company" and "company_document" not in document_types:
        issues.append("Dokumen perusahaan belum diunggah")
    if document.get("resubmission_required"):
        issues.append("Dokumen perbaikan belum diunggah")
    return ("READY" if not issues else "INCOMPLETE", issues)


@buyers_router.post("/register", response_model=BuyerProfile, status_code=201)
async def register_buyer(input: BuyerRegistrationCreate):
    email = input.email.strip().lower()
    existing = await db.buyers.find_one({"email": email})
    if existing:
        return BuyerProfile(**existing)
    buyer_number = await db.buyers.count_documents({}) + 1
    draft = input.model_dump(exclude={"email"}) | {"email": email, "documents": [], "buyer_code": f"MPI-{buyer_number:03d}"}
    screening_status, screening_issues = screen_buyer(draft)
    profile = BuyerProfile(**draft, screening_status=screening_status, screening_issues=screening_issues, verification_status="INCOMPLETE", created_at=datetime.now(timezone.utc))
    await db.buyers.insert_one(profile.model_dump())
    return profile


@buyers_router.get("/status/by-name", response_model=BuyerStatusResponse)
async def get_buyer_status(full_name: str = Query(min_length=2, max_length=100)):
    document = await db.buyers.find_one({"full_name": full_name}, sort=[("created_at", DESCENDING)])
    return BuyerStatusResponse(found=document is not None, profile=BuyerProfile(**document) if document else None)


@buyers_router.post("/{buyer_id}/documents", response_model=BuyerProfile)
async def upload_buyer_document(
    buyer_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
):
    buyer = await db.buyers.find_one({"id": buyer_id})
    if not buyer:
        raise HTTPException(status_code=404, detail="Data peserta tidak ditemukan")
    if document_type not in {"identity_document", "company_document"}:
        raise HTTPException(status_code=400, detail="Jenis dokumen tidak didukung")
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail="Dokumen harus PDF, JPG, atau PNG")
    contents = await file.read(MAX_DOCUMENT_SIZE + 1)
    if len(contents) > MAX_DOCUMENT_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran dokumen maksimal 5 MB")
    if not contents:
        raise HTTPException(status_code=400, detail="Dokumen kosong")
    storage_id = await documents_bucket.upload_from_stream(
        file.filename or f"{document_type}.bin",
        contents,
        metadata={"buyer_id": buyer_id, "document_type": document_type, "content_type": content_type},
    )
    document = BuyerDocument(
        document_type=document_type,
        file_name=file.filename or f"{document_type}.bin",
        content_type=content_type,
        size_bytes=len(contents),
        storage_id=str(storage_id),
        uploaded_at=datetime.now(timezone.utc),
    )
    documents = [item for item in buyer.get("documents", []) if item.get("document_type") != document_type]
    documents.append(document.model_dump())
    updated = buyer | {"documents": documents, "resubmission_required": False}
    screening_status, screening_issues = screen_buyer(updated)
    verification_status = "PENDING" if screening_status == "READY" else "INCOMPLETE"
    await db.buyers.update_one({"id": buyer_id}, {"$set": {"documents": documents, "screening_status": screening_status, "screening_issues": screening_issues, "verification_status": verification_status, "resubmission_required": False, "reviewed_at": None, "reviewed_by": None, "review_reason": None}})
    updated_document = await db.buyers.find_one({"id": buyer_id})
    return BuyerProfile(**updated_document)


@buyers_router.put("/{buyer_id}/resubmit", response_model=BuyerProfile)
async def resubmit_buyer(buyer_id: str, input: BuyerResubmissionUpdate):
    buyer = await db.buyers.find_one({"id": buyer_id})
    if not buyer:
        raise HTTPException(status_code=404, detail="Data peserta tidak ditemukan")
    if buyer.get("verification_status") not in {"REJECTED", "INCOMPLETE"}:
        raise HTTPException(status_code=400, detail="Pengajuan ini tidak dapat dikirim ulang")
    values = input.model_dump() | {
        "email": input.email.strip().lower(),
        "verification_status": "INCOMPLETE",
        "screening_status": "INCOMPLETE",
        "screening_issues": ["Dokumen perbaikan belum diunggah"],
        "resubmission_required": True,
        "reviewed_at": None,
        "reviewed_by": None,
    }
    await db.buyers.update_one({"id": buyer_id}, {"$set": values})
    document = await db.buyers.find_one({"id": buyer_id})
    return BuyerProfile(**document)


@buyers_router.get("/{buyer_id}", response_model=BuyerProfile)
async def get_buyer(buyer_id: str):
    document = await db.buyers.find_one({"id": buyer_id})
    if not document:
        raise HTTPException(status_code=404, detail="Data peserta tidak ditemukan")
    return BuyerProfile(**document)


@wishlist_router.get("", response_model=list[WishlistItem])
async def list_wishlist(bidder_name: str = Query(min_length=2, max_length=80)):
    documents = await db.wishlists.find({"bidder_name": bidder_name}).sort("created_at", DESCENDING).to_list(100)
    items: list[WishlistItem] = []
    for document in documents:
        lot = await db.lots.find_one({"id": document["lot_id"]})
        if lot:
            items.append(WishlistItem(**document, lot_number=lot["lot_number"], title=lot["title"], image_url=lot["image_url"], current_bid=lot["current_bid"], status=lot["status"], auction_end=lot["auction_end"]))
    return items


@wishlist_router.post("/toggle", response_model=WishlistToggleResponse)
async def toggle_wishlist(input: WishlistToggleRequest):
    lot = await db.lots.find_one({"id": input.lot_id})
    if not lot:
        raise HTTPException(status_code=404, detail="Lot tidak ditemukan")
    existing = await db.wishlists.find_one({"bidder_name": input.bidder_name, "lot_id": input.lot_id})
    if existing:
        await db.wishlists.delete_one({"id": existing["id"]})
        return WishlistToggleResponse(lot_id=input.lot_id, liked=False)
    await db.wishlists.insert_one({"id": f"{input.bidder_name.lower().replace(' ', '-')}-{input.lot_id}", "bidder_name": input.bidder_name, "lot_id": input.lot_id, "created_at": datetime.now(timezone.utc)})
    return WishlistToggleResponse(lot_id=input.lot_id, liked=True)