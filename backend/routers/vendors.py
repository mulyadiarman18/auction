from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import DESCENDING, ReturnDocument

from lib.db import db
from models.operations import VendorCreate, VendorDocument, VendorProfile, VendorSettlement, VendorUnitCreate, VendorUnitSubmission


router = APIRouter(prefix="/vendors", tags=["vendors"])
bucket = AsyncIOMotorGridFSBucket(db, bucket_name="vendor_documents")


@router.get("", response_model=list[VendorProfile])
async def list_vendors():
    documents = await db.vendors.find().sort("created_at", DESCENDING).to_list(50)
    return [VendorProfile(**document) for document in documents]


@router.post("/register", response_model=VendorProfile, status_code=201)
async def register_vendor(input: VendorCreate):
    existing = await db.vendors.find_one({"email": input.email.strip().lower()})
    if existing: return VendorProfile(**existing)
    profile = VendorProfile(**input.model_dump(exclude={"email"}), email=input.email.strip().lower(), created_at=datetime.now(timezone.utc))
    await db.vendors.insert_one(profile.model_dump())
    return profile


@router.get("/{vendor_id}", response_model=VendorProfile)
async def get_vendor(vendor_id: str):
    document = await db.vendors.find_one({"id": vendor_id})
    if not document: raise HTTPException(status_code=404, detail="Vendor tidak ditemukan")
    return VendorProfile(**document)


@router.post("/{vendor_id}/documents/{document_type}", response_model=VendorProfile)
async def upload_vendor_document(vendor_id: str, document_type: str, file: UploadFile = File(...)):
    vendor = await db.vendors.find_one({"id": vendor_id})
    if not vendor: raise HTTPException(status_code=404, detail="Vendor tidak ditemukan")
    if document_type not in {"LEGALITY", "PKS"}: raise HTTPException(status_code=400, detail="Jenis dokumen tidak didukung")
    if (file.content_type or "") not in {"application/pdf", "image/jpeg", "image/png"}: raise HTTPException(status_code=400, detail="Dokumen harus PDF, JPG, atau PNG")
    contents = await file.read(5 * 1024 * 1024 + 1)
    if not contents or len(contents) > 5 * 1024 * 1024: raise HTTPException(status_code=400, detail="Ukuran dokumen maksimal 5 MB")
    storage_id = await bucket.upload_from_stream(file.filename or document_type, contents, metadata={"vendor_id": vendor_id, "document_type": document_type})
    document = VendorDocument(document_type=document_type, file_name=file.filename or document_type, content_type=file.content_type or "application/pdf", size_bytes=len(contents), storage_id=str(storage_id), uploaded_at=datetime.now(timezone.utc))
    documents = [item for item in vendor.get("documents", []) if item.get("document_type") != document_type] + [document.model_dump()]
    values = {"documents": documents, "legality_status": "PENDING" if document_type == "LEGALITY" else vendor.get("legality_status", "INCOMPLETE"), "pks_status": "UNDER_REVIEW" if document_type == "PKS" else vendor.get("pks_status", "NOT_UPLOADED")}
    updated = await db.vendors.find_one_and_update({"id": vendor_id}, {"$set": values}, return_document=ReturnDocument.AFTER)
    return VendorProfile(**updated)


@router.get("/{vendor_id}/units", response_model=list[VendorUnitSubmission])
async def vendor_units(vendor_id: str):
    documents = await db.vendor_units.find({"vendor_id": vendor_id}).sort("created_at", DESCENDING).to_list(100)
    return [VendorUnitSubmission(**document) for document in documents]


@router.post("/{vendor_id}/units", response_model=VendorUnitSubmission, status_code=201)
async def submit_vendor_unit(vendor_id: str, input: VendorUnitCreate):
    vendor = await db.vendors.find_one({"id": vendor_id})
    if not vendor: raise HTTPException(status_code=404, detail="Vendor tidak ditemukan")
    if vendor.get("legality_status") != "APPROVED" or vendor.get("pks_status") != "ACTIVE":
        raise HTTPException(status_code=403, detail="Vendor harus terverifikasi dan PKS berstatus ACTIVE")
    submission = VendorUnitSubmission(**input.model_dump(), vendor_id=vendor_id, created_at=datetime.now(timezone.utc))
    await db.vendor_units.insert_one(submission.model_dump())
    return submission


@router.get("/{vendor_id}/settlements", response_model=list[VendorSettlement])
async def vendor_settlements(vendor_id: str):
    vendor = await db.vendors.find_one({"id": vendor_id})
    fee_percent = float(vendor.get("admin_fee_percent", 1.5)) if vendor else 1.5
    units = await db.vendor_units.find({"vendor_id": vendor_id}).sort("created_at", DESCENDING).to_list(100)
    return [VendorSettlement(unit_submission_id=unit["id"], unit_name=unit["unit_name"], status=unit["status"], settlement_status=unit.get("settlement_status", "NONE"), winning_bid=unit.get("winning_bid"), admin_fee_percent=fee_percent, admin_fee_amount=round((unit.get("winning_bid") or 0) * fee_percent / 100), net_settlement=(unit.get("winning_bid") or 0) - round((unit.get("winning_bid") or 0) * fee_percent / 100)) for unit in units]