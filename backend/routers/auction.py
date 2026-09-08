from datetime import datetime, timezone
import re

from fastapi import APIRouter, HTTPException, Query
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from lib.db import db
from models.auction import Bid, BidCreate, Lot


router = APIRouter(prefix="/lots", tags=["lots"])
bids_router = APIRouter(prefix="/bids", tags=["bids"])


def _lot_from_doc(document: dict) -> Lot:
    return Lot(**document)


@router.get("", response_model=list[Lot])
async def list_lots(
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    location: str | None = Query(default=None),
    sort: str = Query(default="ending_soon"),
):
    query: dict = {}
    if category and category != "all":
        query["category"] = category
    if status and status != "all":
        query["status"] = status.upper()
    if search:
        escaped = re.escape(search)
        query["$or"] = [
            {"title": {"$regex": escaped, "$options": "i"}},
            {"lot_number": {"$regex": escaped, "$options": "i"}},
            {"location": {"$regex": escaped, "$options": "i"}},
        ]
    if min_price is not None or max_price is not None:
        query["current_bid"] = {}
        if min_price is not None:
            query["current_bid"]["$gte"] = min_price
        if max_price is not None:
            query["current_bid"]["$lte"] = max_price
    if location and location != "all":
        query["location"] = {"$regex": re.escape(location), "$options": "i"}
    sort_field = "auction_end" if sort not in {"price_asc", "price_desc"} else "current_bid"
    sort_direction = ASCENDING if sort != "price_desc" else DESCENDING
    documents = await db.lots.find(query).sort(sort_field, sort_direction).to_list(100)
    return [_lot_from_doc(document) for document in documents]


@router.get("/{lot_id}", response_model=Lot)
async def get_lot(lot_id: str):
    document = await db.lots.find_one({"id": lot_id})
    if not document:
        raise HTTPException(status_code=404, detail="Lot tidak ditemukan")
    return _lot_from_doc(document)


@router.get("/{lot_id}/bids", response_model=list[Bid])
async def list_lot_bids(lot_id: str):
    if not await db.lots.find_one({"id": lot_id}, {"_id": 1}):
        raise HTTPException(status_code=404, detail="Lot tidak ditemukan")
    documents = await db.bids.find({"lot_id": lot_id}).sort("created_at", DESCENDING).to_list(100)
    return [Bid(**document) for document in documents]


@router.post("/{lot_id}/bids", response_model=Bid, status_code=201)
async def place_bid(lot_id: str, input: BidCreate):
    lot = await db.lots.find_one({"id": lot_id})
    if not lot:
        raise HTTPException(status_code=404, detail="Lot tidak ditemukan")
    now = datetime.now(timezone.utc)
    if lot["status"] != "LIVE" or lot["auction_end"] < now.replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Lelang untuk lot ini sudah tidak aktif")

    minimum_amount = max(lot["base_price"], lot["current_bid"] + lot["minimum_increment"])
    if input.amount < minimum_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Penawaran minimum adalah Rp {minimum_amount:,}".replace(",", "."),
        )

    updated_lot = await db.lots.find_one_and_update(
        {"id": lot_id, "status": "LIVE", "current_bid": lot["current_bid"]},
        {"$set": {"current_bid": input.amount, "current_bidder_name": input.bidder_name}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated_lot:
        raise HTTPException(status_code=409, detail="Lot baru saja menerima penawaran lain, silakan coba lagi")

    bid = Bid(
        lot_id=lot_id,
        bidder_name=input.bidder_name,
        bidder_type=input.bidder_type,
        amount=input.amount,
        created_at=now,
    )
    await db.bids.insert_one(bid.model_dump())
    return bid


@bids_router.get("/mine", response_model=list[Bid])
async def list_my_bids(bidder_name: str = Query(min_length=2, max_length=80)):
    documents = await db.bids.find({"bidder_name": bidder_name}).sort("created_at", DESCENDING).to_list(100)
    return [Bid(**document) for document in documents]