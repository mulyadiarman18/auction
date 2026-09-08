from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import Depends, HTTPException, Request

from lib.db import db
from models.marketplace import AdminUserPublic


SESSION_COOKIE = "lelangoto_admin_session"
SESSION_HOURS = 8


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_admin_session(user_id: str) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(40)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)
    await db.admin_sessions.insert_one({
        "token_hash": hash_session_token(token),
        "user_id": user_id,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc),
    })
    return token, expires_at


async def get_current_admin(request: Request) -> AdminUserPublic:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Login admin diperlukan")
    session = await db.admin_sessions.find_one({
        "token_hash": hash_session_token(token),
        "expires_at": {"$gt": datetime.now(timezone.utc).replace(tzinfo=None)},
    })
    if not session:
        raise HTTPException(status_code=401, detail="Sesi admin tidak valid atau sudah berakhir")
    user = await db.admin_users.find_one({"id": session["user_id"], "is_active": True})
    if not user:
        raise HTTPException(status_code=401, detail="Akun admin tidak aktif")
    return AdminUserPublic(**user)


async def require_super_admin(current: AdminUserPublic = Depends(get_current_admin)) -> AdminUserPublic:
    if current.role != "super_admin":
        raise HTTPException(status_code=403, detail="Aksi ini hanya tersedia untuk Super Admin")
    return current