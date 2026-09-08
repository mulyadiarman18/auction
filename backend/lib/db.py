"""Shared Mongo handle — import `client`/`db` from here (server.py, routers, seed.py)."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, IndexModel

load_dotenv(Path(__file__).parent.parent / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

logger = logging.getLogger(__name__)

# One entry per collection: every field a route filters, sorts, or dedupes on. Applied by ensure_indexes() at startup.
INDEXES: dict[str, list[IndexModel]] = {
    "status_checks": [IndexModel([("timestamp", DESCENDING)], name="timestamp_desc")],
    "lots": [
        IndexModel([("id", ASCENDING)], name="lot_id", unique=True),
        IndexModel([("status", ASCENDING), ("auction_end", ASCENDING)], name="lot_status_end"),
        IndexModel([("category", ASCENDING)], name="lot_category"),
        IndexModel([("location", ASCENDING), ("current_bid", ASCENDING)], name="lot_location_price"),
    ],
    "bids": [
        IndexModel([("lot_id", ASCENDING), ("created_at", DESCENDING)], name="bid_lot_created"),
        IndexModel([("bidder_name", ASCENDING), ("created_at", DESCENDING)], name="bidder_created"),
    ],
    "buyers": [IndexModel([("email", ASCENDING)], name="buyer_email", unique=True)],
    "wishlists": [IndexModel([("bidder_name", ASCENDING), ("lot_id", ASCENDING)], name="wishlist_owner_lot", unique=True)],
    "admin_audit_logs": [IndexModel([("created_at", DESCENDING)], name="audit_created_desc")],
    "admin_users": [IndexModel([("username", ASCENDING)], name="admin_username", unique=True)],
    "admin_sessions": [
        IndexModel([("token_hash", ASCENDING)], name="session_token", unique=True),
        IndexModel([("expires_at", ASCENDING)], name="session_expiry", expireAfterSeconds=0),
    ],
}


async def ensure_indexes() -> None:
    for collection, models in INDEXES.items():
        for model in models:  # one at a time so a bad spec skips only itself
            try:
                await db[collection].create_indexes([model])
            except Exception as exc:  # never block boot on an index; the log line names what to fix
                logger.error("ensure_indexes(%s.%s): %s", collection, model.document["name"], exc)
