import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "zhijian-calendar"


def test_marketplace_and_plugin_manifest_are_consistent():
    plugin = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
    )
    entry = marketplace["plugins"][0]

    assert plugin["name"] == "zhijian-calendar"
    assert plugin["version"] == "1.1.0"
    assert plugin["skills"] == "./skills/"
    assert plugin["mcpServers"] == "./.mcp.json"
    assert "apps" not in plugin
    assert marketplace["name"] == "yuanxin-insight"
    assert entry["name"] == plugin["name"]
    assert entry["source"]["path"] == "./plugins/zhijian-calendar"
    assert entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }


def test_plugin_distributes_the_remote_mcp_server_directly():
    mcp = json.loads((PLUGIN / ".mcp.json").read_text())

    assert mcp == {
        "mcpServers": {
            "zhijian_calendar": {
                "type": "http",
                "url": "https://calendar.yuanxininsight.com/mcp",
            }
        }
    }
    assert not (PLUGIN / ".app.json").exists()


def test_distribution_contains_no_credentials_or_calendar_cache():
    forbidden_names = {"data.json", "state.json", ".env", "config.json"}
    forbidden_text = ("BEGIN PRIVATE KEY", "Bearer eyJ", "zhijian_token")

    for path in ROOT.rglob("*"):
        if not path.is_file() or "tests" in path.parts:
            continue
        assert path.name not in forbidden_names
        if path.suffix in {".json", ".md", ".py"}:
            text = path.read_text()
            assert all(value not in text for value in forbidden_text)
