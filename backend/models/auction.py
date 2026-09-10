from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field


LotStatus = Literal["LIVE", "UPCOMING", "ENDED"]


class Lot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lot_number: str
    title: str
    category: str
    status: LotStatus
    location: str
    image_url: str
    gallery_urls: list[str] = Field(default_factory=list)
    year: int
    mileage: str
    transmission: str
    engine: str
    grade: str
    inspection_score: int
    seller_verified: bool = True
    base_price: int
    current_bid: int
    minimum_increment: int
    auction_start: datetime
    auction_end: datetime
    description: str
    features: list[str] = Field(default_factory=list)
    vin: str
    document_status: str
    auction_code: str = "LLG-20260910-01"
    unit_number: str = ""
    hull_number: str = ""
    registration_code: str = ""
    brand: str = ""
    model_type: str = ""
    operating_hours: str = ""
    seller_name: str = "MPI Verified Vendor"
    pool_location: str = ""
    document_completeness: list[str] = Field(default_factory=list)
    session_id: str | None = None
    unit_status: Literal["DRAFT", "VERIFIED", "READY", "IN_AUCTION", "SOLD", "UNSOLD", "HANDED_OVER", "WITHDRAWN"] = "READY"
    inspection_status: Literal["UNSCHEDULED", "SCHEDULED", "IN_PROGRESS", "COMPLETED", "REJECTED"] = "COMPLETED"
    reserve_price: int = 0


class BidCreate(BaseModel):
    bidder_name: str = Field(min_length=2, max_length=80)
    bidder_type: str = Field(default="Verified Bidder", min_length=2, max_length=40)
    amount: int = Field(gt=0)


class Bid(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lot_id: str
    bidder_name: str
    bidder_type: str
    amount: int
    created_at: datetime
    status: Literal["VALID", "OUTBID"] = "VALID"
    bidder_code: str = ""