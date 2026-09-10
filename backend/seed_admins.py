import asyncio
import os
import uuid

import bcrypt

from lib.db import client, db, ensure_indexes


async def upsert_admin(username: str, password: str, name: str, role: str) -> None:
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    await db.admin_users.update_one(
        {"username": username.lower()},
        {"$set": {"name": name, "role": role, "password_hash": password_hash, "is_active": True}, "$setOnInsert": {"id": str(uuid.uuid4()), "username": username.lower()}},
        upsert=True,
    )


async def seed() -> None:
    required = ["ADMIN_SUPER_USERNAME", "ADMIN_SUPER_PASSWORD", "ADMIN_REVIEWER_USERNAME", "ADMIN_REVIEWER_PASSWORD", "ADMIN_FINANCE_USERNAME", "ADMIN_FINANCE_PASSWORD", "ADMIN_INSPECTOR_USERNAME", "ADMIN_INSPECTOR_PASSWORD"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    await upsert_admin(os.environ["ADMIN_SUPER_USERNAME"], os.environ["ADMIN_SUPER_PASSWORD"], "Dina Super Admin", "super_admin")
    await upsert_admin(os.environ["ADMIN_REVIEWER_USERNAME"], os.environ["ADMIN_REVIEWER_PASSWORD"], "Raka Reviewer", "reviewer")
    await upsert_admin(os.environ["ADMIN_FINANCE_USERNAME"], os.environ["ADMIN_FINANCE_PASSWORD"], "Fina Finance MPI", "finance")
    await upsert_admin(os.environ["ADMIN_INSPECTOR_USERNAME"], os.environ["ADMIN_INSPECTOR_PASSWORD"], "Indra Inspektor", "inspector")
    await ensure_indexes()
    client.close()
    print("Seeded Super Admin and Reviewer accounts")


if __name__ == "__main__":
    asyncio.run(seed())