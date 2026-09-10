"""Server-side date helpers. The pod clock is UTC — anchor "today" here, never in the browser."""

import os
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def today_iso(tz: str | None = None) -> str:
    """Today's date as YYYY-MM-DD in `tz` (default: APP_TZ env, else UTC)."""
    zone = tz or os.environ.get("APP_TZ", "UTC")
    return datetime.now(ZoneInfo(zone)).strftime("%Y-%m-%d")


def default_auction_slots(count: int = 4, include_previous: bool = False) -> list[dict]:
    """Return Tuesday/Friday 10:00-15:00 WIB slots anchored on the server clock."""
    jakarta = ZoneInfo("Asia/Jakarta")
    now = datetime.now(jakarta)
    cursor = now.date() - timedelta(days=7 if include_previous else 0)
    slots: list[dict] = []
    while len(slots) < count:
        if cursor.weekday() in {1, 4}:  # Tuesday, Friday
            start_local = datetime.combine(cursor, time(10, 0), jakarta)
            end_local = datetime.combine(cursor, time(15, 0), jakarta)
            publication_local = start_local - timedelta(days=3)
            if include_previous or end_local >= now:
                status = "CLOSED" if now >= end_local else "LIVE" if start_local <= now < end_local else "PUBLISHED" if now >= publication_local else "DRAFT"
                slots.append({
                    "start_at": start_local.astimezone(timezone.utc).replace(tzinfo=None),
                    "end_at": end_local.astimezone(timezone.utc).replace(tzinfo=None),
                    "publication_at": publication_local.astimezone(timezone.utc).replace(tzinfo=None),
                    "status": status,
                    "local_date": cursor.isoformat(),
                })
        cursor += timedelta(days=1)
    return slots[-count:] if include_previous else slots
