#!/usr/bin/env python3
"""Bind a registered production MCP app to a copied plugin release tree."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

APP_ID_PATTERN = re.compile(r"^asdk_app_[A-Za-z0-9_-]+$")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: bind_registered_app.py PATH_TO_PLUGIN/.app.json", file=sys.stderr)
        return 2

    app_id = os.environ.get("CALENDAR_PRODUCTION_MCP_APP_ID", "")
    if APP_ID_PATTERN.fullmatch(app_id) is None:
        print(
            "CALENDAR_PRODUCTION_MCP_APP_ID must be a registered "
            "asdk_app ID",
            file=sys.stderr,
        )
        return 2

    app_path = Path(sys.argv[1]).resolve()
    plugin_root = app_path.parent
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        print(f"plugin manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text())
    manifest["apps"] = "./.app.json"
    app_manifest = {
        "apps": {
            "zhijian_calendar": {
                "id": app_id,
                "category": "Calendar context",
            }
        }
    }
    app_path.write_text(json.dumps(app_manifest, indent=2, ensure_ascii=False) + "\n")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Bound registered app {app_id} in {plugin_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
