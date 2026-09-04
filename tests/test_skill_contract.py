from pathlib import Path

SKILL = (
    Path(__file__).parents[1]
    / "plugins"
    / "zhijian-calendar"
    / "skills"
    / "schedule-query"
    / "SKILL.md"
)


def _contents() -> tuple[dict[str, str], str]:
    contents = SKILL.read_text()
    _, frontmatter, body = contents.split("---", 2)
    parsed = {}
    for line in frontmatter.strip().splitlines():
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed, body


def test_skill_has_narrow_trigger_and_read_only_tools():
    frontmatter, body = _contents()

    assert frontmatter["name"] == "schedule-query"
    assert frontmatter["description"].startswith("Use when ")
    assert {"list_events", "search_events", "get_sync_status"} <= set(body.split())
    assert "Use only these read-only tools" in body
    assert "create_event" not in body
    assert "update_event" not in body
    assert "delete_event" not in body


def test_skill_defines_time_freshness_and_auth_behavior():
    _, body = _contents()

    for required in (
        "Asia/Shanghai",
        "31",
        "data_as_of",
        "AUTH_REQUIRED",
        "FORBIDDEN",
        "DATA_NOT_READY",
        "UPSTREAM_AUTH_REQUIRED",
        "TEMP_UNAVAILABLE",
    ):
        assert required in body
