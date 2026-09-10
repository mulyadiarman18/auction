from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field


SessionStatus = Literal["DRAFT", "PUBLISHED", "LIVE", "CLOSED"]


class AuctionSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    title: str
    start_at: datetime
    end_at: datetime
    publication_at: datetime
    status: SessionStatus
    lot_ids: list[str] = Field(default_factory=list)
    created_at: datetime


class AuctionSessionUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    status: SessionStatus | None = None
    lot_ids: list[str] | None = None


class BidAccessStatus(BaseModel):
    bidder_name: str
    buyer_id: str | None = None
    verification_status: str = "NOT_REGISTERED"
    membership_status: str = "INACTIVE"
    deposit_status: str = "NOT_SUBMITTED"
    deposit_amount: int = 3_000_000
    eligible: bool = False
    reasons: list[str] = Field(default_factory=list)


class DepositReviewItem(BaseModel):
    buyer_id: str
    bidder_name: str
    email: str
    amount: int
    status: str
    document_file_name: str
    submitted_at: datetime


class DepositReviewUpdate(BaseModel):
    status: Literal["CONFIRMED", "REJECTED"]
    reason: str = Field(default="", max_length=300)


class VendorDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: Literal["LEGALITY", "PKS"]
    file_name: str
    content_type: str
    size_bytes: int
    storage_id: str
    uploaded_at: datetime


class VendorCreate(BaseModel):
    company_name: str = Field(min_length=3, max_length=140)
    tax_number: str = Field(min_length=5, max_length=40)
    address: str = Field(min_length=5, max_length=240)
    pic_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=120)
    phone: str = Field(min_length=8, max_length=30)


class VendorProfile(VendorCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    legality_status: Literal["INCOMPLETE", "PENDING", "APPROVED", "REJECTED"] = "INCOMPLETE"
    pks_status: Literal["NOT_UPLOADED", "UNDER_REVIEW", "ACTIVE", "EXPIRED"] = "NOT_UPLOADED"
    documents: list[VendorDocument] = Field(default_factory=list)
    created_at: datetime
    seller_code: str = ""
    admin_fee_percent: float = 1.5
    contract_number: str = ""
    contract_start: datetime | None = None
    contract_end: datetime | None = None
    pool_address: str = ""
    pool_pic: str = ""
    settlement_terms: str = "3 hari kerja setelah pelunasan pembeli"


class VendorUnitCreate(BaseModel):
    unit_name: str = Field(min_length=3, max_length=160)
    category: str = Field(min_length=2, max_length=80)
    brand: str = Field(min_length=2, max_length=80)
    model_type: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1980, le=2100)
    unit_number: str = Field(min_length=2, max_length=60)
    hull_number: str = Field(min_length=2, max_length=60)
    operating_hours: str = Field(min_length=1, max_length=40)
    pool_location: str = Field(min_length=3, max_length=160)
    proposed_price: int = Field(gt=0)


class VendorUnitSubmission(VendorUnitCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vendor_id: str
    status: Literal["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "LOTTED"] = "SUBMITTED"
    settlement_status: Literal["NONE", "PENDING", "INVOICED", "PAID"] = "NONE"
    winning_bid: int | None = None
    created_at: datetime


class VendorSettlement(BaseModel):
    unit_submission_id: str
    unit_name: str
    status: str
    settlement_status: str
    winning_bid: int | None = None
    admin_fee_percent: float = 1.5
    admin_fee_amount: int = 0
    net_settlement: int = 0


class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    buyer_id: str
    bidder_name: str
    lot_id: str
    lot_title: str
    hammer_price: int
    deposit_deduction: int = 3_000_000
    buyer_admin_fee: int = 0
    tax_amount: int = 0
    total_due: int
    due_at: datetime
    status: Literal["PENDING_PAYMENT", "PAYMENT_REVIEW", "PAID", "OVERDUE", "CANCELLED"] = "PENDING_PAYMENT"
    payment_document: dict | None = None
    created_at: datetime


class InspectionRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lot_id: str
    inspector_name: str
    planned_at: datetime
    status: Literal["UNSCHEDULED", "SCHEDULED", "IN_PROGRESS", "COMPLETED", "REJECTED"] = "SCHEDULED"
    component_scores: dict[str, int] = Field(default_factory=dict)
    notes: str = ""
    total_score: int | None = None
    suggested_grade: Literal["A", "B", "C", "D"] | None = None
    completed_at: datetime | None = None
    photos: list[dict] = Field(default_factory=list)


class InspectionSubmit(BaseModel):
    component_scores: dict[str, int]
    notes: str = Field(default="", max_length=1000)