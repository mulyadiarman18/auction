from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field, model_validator

from models.auction import LotStatus


class BuyerRegistrationCreate(BaseModel):
    buyer_type: Literal["individual", "company"]
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=120)
    phone: str = Field(min_length=8, max_length=30)
    identity_number: str = Field(default="", max_length=40)
    company_name: str | None = Field(default=None, max_length=120)
    tax_number: str = Field(default="", max_length=40)
    address: str = Field(min_length=5, max_length=240)


class BuyerProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buyer_type: Literal["individual", "company"]
    full_name: str
    email: str
    phone: str
    identity_number: str = ""
    company_name: str | None = None
    tax_number: str = ""
    address: str
    verification_status: Literal["INCOMPLETE", "PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED"] = "INCOMPLETE"
    screening_status: Literal["INCOMPLETE", "READY"] = "INCOMPLETE"
    screening_issues: list[str] = Field(default_factory=list)
    documents: list["BuyerDocument"] = Field(default_factory=list)
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    review_reason: str | None = None
    resubmission_required: bool = False


class BuyerVerificationUpdate(BaseModel):
    verification_status: Literal["APPROVED", "REJECTED"]
    admin_name: str = Field(min_length=2, max_length=80)
    reason: str = Field(default="", max_length=300)

    @model_validator(mode="after")
    def require_rejection_reason(self):
        if self.verification_status == "REJECTED" and len(self.reason.strip()) < 5:
            raise ValueError("Alasan penolakan minimal 5 karakter")
        return self


class BuyerResubmissionUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=120)
    phone: str = Field(min_length=8, max_length=30)
    identity_number: str = Field(min_length=5, max_length=40)
    company_name: str | None = Field(default=None, max_length=120)
    tax_number: str = Field(default="", max_length=40)
    address: str = Field(min_length=5, max_length=240)


class BuyerDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: Literal["identity_document", "company_document"]
    file_name: str
    content_type: str
    size_bytes: int
    storage_id: str
    uploaded_at: datetime


class BuyerStatusResponse(BaseModel):
    found: bool
    profile: BuyerProfile | None = None


class AdminAuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: Literal["BUYER"] = "BUYER"
    entity_id: str
    entity_name: str
    action: Literal["APPROVE", "REJECT"]
    admin_name: str
    admin_role: Literal["super_admin", "reviewer"]
    old_status: str
    new_status: str
    reason: str
    created_at: datetime


class AdminUserPublic(BaseModel):
    id: str
    username: str
    name: str
    role: Literal["super_admin", "reviewer"]
    is_active: bool = True


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=120)


class AdminSessionResponse(BaseModel):
    user: AdminUserPublic
    expires_at: datetime


class WishlistToggleRequest(BaseModel):
    bidder_name: str = Field(min_length=2, max_length=80)
    lot_id: str


class WishlistToggleResponse(BaseModel):
    lot_id: str
    liked: bool


class WishlistItem(BaseModel):
    id: str
    bidder_name: str
    lot_id: str
    lot_number: str
    title: str
    image_url: str
    current_bid: int
    status: LotStatus
    auction_end: datetime
    created_at: datetime


class AdminSummary(BaseModel):
    total_lots: int
    live_lots: int
    upcoming_lots: int
    ended_lots: int
    total_bids: int
    total_bid_value: int
    pending_buyers: int


class AdminLotUpdate(BaseModel):
    status: LotStatus | None = None
    auction_start: datetime | None = None
    auction_end: datetime | None = None


class AdminWinner(BaseModel):
    lot_id: str
    lot_number: str
    title: str
    status: Literal["PENDING", "WON", "UNSOLD"]
    bidder_name: str | None = None
    winning_bid: int | None = None
    auction_end: datetime