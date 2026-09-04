import json
import os
import shutil
import subprocess
import sys
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
    assert plugin["version"] == "1.0.0"
    assert plugin["skills"] == "./skills/"
    app_manifest = PLUGIN / ".app.json"
    if app_manifest.exists():
        assert plugin["apps"] == "./.app.json"
    else:
        assert "apps" not in plugin
    assert marketplace["name"] == "yuanxin-insight"
    assert entry["name"] == plugin["name"]
    assert entry["source"]["path"] == "./plugins/zhijian-calendar"
    assert entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }


def test_app_binding_generator_requires_registered_asdk_id(tmp_path):
    script = ROOT / "scripts" / "bind_registered_app.py"
    missing = subprocess.run(
        [sys.executable, str(script), str(tmp_path / ".app.json")],
        capture_output=True,
        text=True,
        check=False,
    )
    invalid = subprocess.run(
        [sys.executable, str(script), str(tmp_path / ".app.json")],
        env={"CALENDAR_PRODUCTION_MCP_APP_ID": "not-registered"},
        capture_output=True,
        text=True,
        check=False,
    )
    plugin_page_id = subprocess.run(
        [sys.executable, str(script), str(tmp_path / ".app.json")],
        env={
            "CALENDAR_PRODUCTION_MCP_APP_ID": "plugin_asdk_app_registered123"
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert missing.returncode != 0
    assert invalid.returncode != 0
    assert plugin_page_id.returncode != 0
    assert not (tmp_path / ".app.json").exists()


def test_app_binding_generator_builds_release_manifest(tmp_path):
    plugin = tmp_path / "zhijian-calendar"
    shutil.copytree(PLUGIN, plugin)
    app_manifest = plugin / ".app.json"
    env = os.environ.copy()
    env["CALENDAR_PRODUCTION_MCP_APP_ID"] = "asdk_app_registered123"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "bind_registered_app.py"),
            str(app_manifest),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    manifest = json.loads(
        (plugin / ".codex-plugin" / "plugin.json").read_text()
    )
    app = json.loads(app_manifest.read_text())
    assert result.returncode == 0
    assert manifest["apps"] == "./.app.json"
    assert app == {
        "apps": {
            "zhijian_calendar": {
                "id": "asdk_app_registered123",
                "category": "Calendar context",
            }
        }
    }


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
