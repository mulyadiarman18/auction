from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field

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
    verification_status: Literal["PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED"] = "PENDING"
    created_at: datetime


class BuyerVerificationUpdate(BaseModel):
    verification_status: Literal["APPROVED", "REJECTED"]


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