from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import DESCENDING, ReturnDocument

from lib.admin_auth import require_inspector
from lib.db import db
from models.marketplace import AdminUserPublic
from models.operations import InspectionRecord, InspectionSubmit


router = APIRouter(prefix="/admin/inspections", tags=["inspections"])
bucket = AsyncIOMotorGridFSBucket(db, bucket_name="inspection_photos")
PHOTO_SLOTS = {"front", "rear", "left", "right", "dashboard", "engine", "frame_number", "damage"}


@router.get("", response_model=list[InspectionRecord])
async def list_inspections(current: AdminUserPublic = Depends(require_inspector)):
    query = {} if current.role == "super_admin" else {"inspector_name": current.name}
    documents = await db.inspections.find(query).sort("planned_at", DESCENDING).to_list(100)
    return [InspectionRecord(**document) for document in documents]


@router.patch("/{inspection_id}", response_model=InspectionRecord)
async def submit_inspection(inspection_id: str, input: InspectionSubmit, current: AdminUserPublic = Depends(require_inspector)):
    record = await db.inspections.find_one({"id": inspection_id})
    if not record: raise HTTPException(status_code=404, detail="Tugas inspeksi tidak ditemukan")
    scores = [max(0, min(100, int(value))) for value in input.component_scores.values()]
    if len(scores) < 5: raise HTTPException(status_code=400, detail="Minimal 5 kelompok komponen harus dinilai")
    total = round(sum(scores) / len(scores)); grade = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 50 else "D"
    updated = await db.inspections.find_one_and_update({"id": inspection_id}, {"$set": {"component_scores": input.component_scores, "notes": input.notes, "total_score": total, "suggested_grade": grade, "status": "COMPLETED", "completed_at": datetime.now(timezone.utc)}}, return_document=ReturnDocument.AFTER)
    await db.lots.update_one({"id": record["lot_id"]}, {"$set": {"inspection_status": "COMPLETED", "inspection_score": total, "grade": f"Grade {grade}", "unit_status": "VERIFIED"}})
    return InspectionRecord(**updated)


@router.post("/{inspection_id}/photos/{slot}", response_model=InspectionRecord)
async def upload_inspection_photo(inspection_id: str, slot: str, file: UploadFile = File(...), current: AdminUserPublic = Depends(require_inspector)):
    record = await db.inspections.find_one({"id": inspection_id})
    if not record: raise HTTPException(status_code=404, detail="Tugas inspeksi tidak ditemukan")
    if slot not in PHOTO_SLOTS: raise HTTPException(status_code=400, detail="Slot foto tidak didukung")
    if (file.content_type or "") not in {"image/jpeg", "image/png"}: raise HTTPException(status_code=400, detail="Foto harus JPG atau PNG")
    contents = await file.read(5 * 1024 * 1024 + 1)
    if not contents or len(contents) > 5 * 1024 * 1024: raise HTTPException(status_code=400, detail="Ukuran foto maksimal 5 MB")
    storage_id = await bucket.upload_from_stream(file.filename or slot, contents, metadata={"inspection_id": inspection_id, "slot": slot, "uploaded_by": current.name})
    photos = [photo for photo in record.get("photos", []) if photo.get("slot") != slot]
    photos.append({"slot": slot, "file_name": file.filename or slot, "storage_id": str(storage_id), "content_type": file.content_type, "uploaded_by": current.name, "uploaded_at": datetime.now(timezone.utc)})
    updated = await db.inspections.find_one_and_update({"id": inspection_id}, {"$set": {"photos": photos, "status": "IN_PROGRESS"}}, return_document=ReturnDocument.AFTER)
    return InspectionRecord(**updated)