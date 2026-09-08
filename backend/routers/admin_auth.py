from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from lib.admin_auth import SESSION_COOKIE, SESSION_HOURS, create_admin_session, get_current_admin, hash_session_token
from lib.db import db
from models.marketplace import AdminLoginRequest, AdminSessionResponse, AdminUserPublic


router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


@router.post("/login", response_model=AdminSessionResponse)
async def admin_login(input: AdminLoginRequest, response: Response):
    user = await db.admin_users.find_one({"username": input.username.strip().lower(), "is_active": True})
    if not user or not bcrypt.checkpw(input.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Username atau password salah")
    token, expires_at = await create_admin_session(user["id"])
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_HOURS * 3600,
        expires=expires_at,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return AdminSessionResponse(user=AdminUserPublic(**user), expires_at=expires_at)


@router.get("/me", response_model=AdminUserPublic)
async def admin_me(current: AdminUserPublic = Depends(get_current_admin)):
    return current


@router.post("/logout", status_code=204)
async def admin_logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        await db.admin_sessions.delete_one({"token_hash": hash_session_token(token)})
    response.delete_cookie(SESSION_COOKIE, path="/")