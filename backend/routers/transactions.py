from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import DESCENDING, ReturnDocument

from lib.admin_auth import require_finance
from lib.db import db
from models.marketplace import AdminUserPublic, DepositDocument
from models.operations import DepositReviewUpdate, Invoice


router = APIRouter(prefix="/transactions", tags=["transactions"])
admin_router = APIRouter(prefix="/admin/invoices", tags=["admin-invoices"])
bucket = AsyncIOMotorGridFSBucket(db, bucket_name="payment_documents")


@router.get("", response_model=list[Invoice])
async def member_transactions(bidder_name: str = Query(min_length=2, max_length=100)):
    documents = await db.invoices.find({"bidder_name": bidder_name}).sort("created_at", DESCENDING).to_list(100)
    return [Invoice(**document) for document in documents]


@router.post("/{invoice_id}/proof", response_model=Invoice)
async def upload_payment_proof(invoice_id: str, file: UploadFile = File(...)):
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice: raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    contents = await file.read(5 * 1024 * 1024 + 1)
    if not contents or len(contents) > 5 * 1024 * 1024: raise HTTPException(status_code=400, detail="Bukti pembayaran maksimal 5 MB")
    storage_id = await bucket.upload_from_stream(file.filename or "payment-proof", contents)
    document = DepositDocument(file_name=file.filename or "payment-proof", content_type=file.content_type or "application/pdf", size_bytes=len(contents), storage_id=str(storage_id), uploaded_at=datetime.now(timezone.utc))
    updated = await db.invoices.find_one_and_update({"id": invoice_id}, {"$set": {"status": "PAYMENT_REVIEW", "payment_document": document.model_dump()}}, return_document=ReturnDocument.AFTER)
    return Invoice(**updated)


@admin_router.get("", response_model=list[Invoice])
async def finance_invoices(current: AdminUserPublic = Depends(require_finance)):
    documents = await db.invoices.find().sort("created_at", DESCENDING).to_list(100)
    return [Invoice(**document) for document in documents]


@admin_router.patch("/{invoice_id}", response_model=Invoice)
async def review_invoice(invoice_id: str, input: DepositReviewUpdate, current: AdminUserPublic = Depends(require_finance)):
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice: raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    status = "PAID" if input.status == "CONFIRMED" else "PENDING_PAYMENT"
    updated = await db.invoices.find_one_and_update({"id": invoice_id}, {"$set": {"status": status, "reviewed_at": datetime.now(timezone.utc), "reviewed_by": current.name}}, return_document=ReturnDocument.AFTER)
    return Invoice(**updated)


@admin_router.post("/seed-winner/{lot_id}", response_model=Invoice)
async def create_winner_invoice(lot_id: str, buyer_id: str, current: AdminUserPublic = Depends(require_finance)):
    lot = await db.lots.find_one({"id": lot_id}); buyer = await db.buyers.find_one({"id": buyer_id})
    if not lot or not buyer: raise HTTPException(status_code=404, detail="Lot atau buyer tidak ditemukan")
    hammer = int(lot["current_bid"]); deposit = int(buyer.get("deposit_amount", 3_000_000))
    invoice = Invoice(invoice_number=f"INV/{datetime.now().year}/{datetime.now().month:02d}/{await db.invoices.count_documents({}) + 1:04d}", buyer_id=buyer_id, bidder_name=buyer["full_name"], lot_id=lot_id, lot_title=lot["title"], hammer_price=hammer, deposit_deduction=deposit, total_due=hammer - deposit, due_at=datetime.now(timezone.utc) + timedelta(days=3), created_at=datetime.now(timezone.utc))
    await db.invoices.insert_one(invoice.model_dump()); return invoice