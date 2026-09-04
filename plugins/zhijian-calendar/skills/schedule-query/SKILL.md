---
name: schedule-query
description: Use when a user asks to find, list, or check shared organization calendar events by Beijing date, relative date, week, keyword, or sync freshness.
---

# Shared schedule query

Use only these read-only tools:

- list_events for a date or inclusive date range.
- search_events for a keyword plus an optional date range.
- get_sync_status when the user asks about freshness or a result is stale.

Interpret today, tomorrow, weekdays, and weeks in Asia/Shanghai (Beijing time, UTC+8). Send dates as YYYY-MM-DD. A requested range is inclusive and may not exceed 31 days; split a longer request into adjacent ranges.

Request additional pages only when needed to answer the question. Group results by Beijing date. Preserve all-day events as all-day and never invent a start time or missing field. Treat the service response as read-only; do not modify, create, or delete calendar data.

When `stale` is true, disclose that briefly and render `data_as_of` in Beijing time. Do not claim freshness beyond the returned status.

Handle service errors without exposing authorization internals:

- AUTH_REQUIRED: ask the user to connect or reconnect Feishu.
- FORBIDDEN: say this account does not currently have access; do not reveal tenant or allowlist details.
- DATA_NOT_READY: say the shared calendar is not ready and suggest trying later.
- UPSTREAM_AUTH_REQUIRED: say an administrator must renew the calendar source connection.
- TEMP_UNAVAILABLE: say the service is temporarily unavailable and suggest retrying.

Never use shell commands or local cache/configuration files as an alternate calendar source.
