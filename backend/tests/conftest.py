"""Pre-scaffolded pytest fixtures for the FastAPI backend.

Tests hit the live uvicorn process managed by supervisor (not an in-process ASGI app), so
the app under test is the same one the frontend and Playwright see. Do NOT re-create this
file — add app-specific fixtures below the marker at the bottom.
"""

import os

import httpx
import pytest
import pytest_asyncio

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"


def api_url(path: str = "") -> str:
    """Absolute URL for an /api route: api_url("/status") -> http://localhost:8001/api/status."""
    return f"{API_URL}{path}"


@pytest.fixture(scope="session")
def backend_url() -> str:
    return BACKEND_URL


@pytest.fixture
def client():
    """Sync httpx client rooted at /api — the default for endpoint tests.

    Example:
        def test_status(client):
            assert client.get("/status").status_code == 200
    """
    with httpx.Client(base_url=API_URL, timeout=30.0) as c:
        yield c


@pytest_asyncio.fixture
async def aclient():
    """Async variant, for tests that also await motor/backend helpers directly."""
    async with httpx.AsyncClient(base_url=API_URL, timeout=30.0) as c:
        yield c


# --- app-specific fixtures below this line ---

SESSION_COOKIE_NAME = "lelangoto_admin_session"


@pytest.fixture
def login_as():
    return admin_login


def admin_login(client: httpx.Client, username: str, password: str) -> dict:
    """Log in and return {"user": ..., "cookie_header": "name=value"}.

    The app sets its session cookie with Secure=true (correct for the https
    preview deployment). httpx's cookie jar follows RFC 6265 strictly and
    will not attach a Secure cookie back on a plain http://localhost
    request (unlike browsers, which special-case localhost as a secure
    context). We extract the raw token and attach it manually via the
    Cookie header so backend tests can exercise the authenticated flow
    over http://localhost:8001 exactly like the wiring contract requires.
    """
    resp = client.post("/admin/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.cookies.get(SESSION_COOKIE_NAME)
    assert token, "login did not return a session cookie"
    return {"user": resp.json()["user"], "cookie_header": f"{SESSION_COOKIE_NAME}={token}"}
