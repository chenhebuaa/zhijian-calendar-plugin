from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import StreamableHTTPError, streamablehttp_client

BASE_URL = os.getenv("CALENDAR_E2E_BASE_URL", "").rstrip("/")
ALLOWED_SESSION = os.getenv("CALENDAR_E2E_ALLOWED_SESSION", "")
ADMIN_SESSION = os.getenv("CALENDAR_E2E_ADMIN_SESSION", "")
DENIED_SESSION = os.getenv("CALENDAR_E2E_DENIED_SESSION", "")
FIXTURE_OPEN_ID = os.getenv("CALENDAR_E2E_FIXTURE_OPEN_ID", "")

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not (BASE_URL and ALLOWED_SESSION and ADMIN_SESSION),
        reason=(
            "staging E2E requires CALENDAR_E2E_BASE_URL, "
            "CALENDAR_E2E_ALLOWED_SESSION, and CALENDAR_E2E_ADMIN_SESSION"
        ),
    ),
]

SENSITIVE_FIELDS = ("title", "note", "start_at", "end_at")


@asynccontextmanager
async def calendar_session(token: str) -> AsyncIterator[ClientSession]:
    headers = {"Authorization": f"Bearer {token}"}
    async with (
        streamablehttp_client(f"{BASE_URL}/mcp", headers=headers) as streams,
        ClientSession(streams[0], streams[1]) as session,
    ):
        await session.initialize()
        yield session


def serialized(value: object) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=False, default=str)


@pytest.mark.asyncio
async def test_oauth_discovery_and_unauthenticated_denial():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        discovery = await client.get("/.well-known/oauth-protected-resource/mcp")
        denied = await client.post(
            "/mcp",
            headers={"Accept": "application/json, text/event-stream"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "calendar-e2e", "version": "1"},
                },
            },
        )

    assert discovery.status_code == 200
    assert denied.status_code in {401, 403}
    assert all(field not in denied.text for field in SENSITIVE_FIELDS)


@pytest.mark.asyncio
async def test_denied_session_cannot_read_event_fields():
    if not DENIED_SESSION:
        pytest.skip("CALENDAR_E2E_DENIED_SESSION is required for denied-user proof")

    with pytest.raises(StreamableHTTPError) as caught:
        async with calendar_session(DENIED_SESSION) as session:
            await session.call_tool(
                "list_events",
                {"start_date": "2026-09-03", "end_date": "2026-09-03"},
            )
    assert all(field not in str(caught.value) for field in SENSITIVE_FIELDS)


@pytest.mark.asyncio
async def test_allowed_tools_and_range_boundary():
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    async with calendar_session(ALLOWED_SESSION) as session:
        listed = await session.call_tool(
            "list_events",
            {"start_date": str(today), "end_date": str(today + timedelta(days=30))},
        )
        too_wide = await session.call_tool(
            "list_events",
            {"start_date": str(today), "end_date": str(today + timedelta(days=31))},
        )
        searched = await session.call_tool("search_events", {"query": "E2E"})
        status = await session.call_tool("get_sync_status", {})

    assert not listed.isError
    assert too_wide.isError
    assert not searched.isError
    assert not status.isError
    assert "stale" in serialized(listed)
    assert "data_as_of" in serialized(listed)


@pytest.mark.asyncio
async def test_revocation_is_effective_on_next_call():
    if not FIXTURE_OPEN_ID:
        pytest.skip("CALENDAR_E2E_FIXTURE_OPEN_ID is required for revocation proof")

    headers = {
        "Authorization": f"Bearer {ADMIN_SESSION}",
        "X-Correlation-ID": "calendar-e2e-revocation",
    }
    async with calendar_session(ALLOWED_SESSION) as session:
        before = await session.call_tool(
            "list_events",
            {"start_date": "2026-09-03", "end_date": "2026-09-03"},
        )
        assert not before.isError
        async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
            disabled = await client.post(
                f"/admin/users/{FIXTURE_OPEN_ID}/disable"
            )
            assert disabled.status_code == 200
            try:
                with pytest.raises(StreamableHTTPError):
                    await session.call_tool(
                        "list_events",
                        {
                            "start_date": "2026-09-03",
                            "end_date": "2026-09-03",
                        },
                    )
            finally:
                enabled = await client.post(
                    f"/admin/users/{FIXTURE_OPEN_ID}/enable"
                )
                assert enabled.status_code == 200
