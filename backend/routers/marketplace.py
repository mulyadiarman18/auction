from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pymongo import DESCENDING

from lib.db import db
from models.marketplace import (
    BuyerProfile,
    BuyerRegistrationCreate,
    WishlistItem,
    WishlistToggleRequest,
    WishlistToggleResponse,
)


buyers_router = APIRouter(prefix="/buyers", tags=["buyers"])
wishlist_router = APIRouter(prefix="/wishlists", tags=["wishlists"])


@buyers_router.post("/register", response_model=BuyerProfile, status_code=201)
async def register_buyer(input: BuyerRegistrationCreate):
    email = input.email.strip().lower()
    existing = await db.buyers.find_one({"email": email})
    if existing:
        return BuyerProfile(**existing)
    profile = BuyerProfile(**input.model_dump(exclude={"email"}), email=email, created_at=datetime.now(timezone.utc))
    await db.buyers.insert_one(profile.model_dump())
    return profile


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