#!/usr/bin/env python3
"""Convert source/scenarios/*.yaml → ECI.TestHarness/scenarios/*.json.

The runtime harness reads JSON via SMAPI's Helper.Data, so we author in
YAML (consistent with simulator scenarios + dialogue YAML) and let this
script emit the JSON that SMAPI expects.

YAML schema (flat list of scenario objects):
    - name: "Linus sentinel after meeting"
      setup:
        time: 1900            # optional Stardew HHMM
        warp_player_to: Mountain
        hearts:
          Linus: 4
      assert:
        npc: Linus
        text_contains: "[ECI sentinel]"

Run: python3 tools/build_scenarios.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "source" / "scenarios"
OUT = REPO / "ECI.TestHarness" / "scenarios"


# --- snake_case (yaml) → PascalCase (C# JSON) -----------------------------

KEY_MAP_SETUP = {
    "time": "Time",
    "weather": "Weather",
    "hearts": "Hearts",
    "warp_player_to": "WarpPlayerTo",
}
KEY_MAP_ASSERT = {
    "npc": "Npc",
    "text_contains": "TextContains",
    "text_equals": "TextEquals",
}


def transform_scenario(sc: dict) -> dict:
    out: dict = {"Name": sc.get("name", "")}
    setup = sc.get("setup")
    if setup:
        out["Setup"] = {KEY_MAP_SETUP.get(k, k): v for k, v in setup.items()}
    if "assert" in sc:
        a = sc["assert"]
        out["Assert"] = {KEY_MAP_ASSERT.get(k, k): v for k, v in a.items()}
    return out


def main() -> int:
    if not SOURCE.exists():
        print(f"(no source/scenarios/ — nothing to build)", file=sys.stderr)
        return 0
    OUT.mkdir(parents=True, exist_ok=True)

    yaml_files = sorted(SOURCE.glob("*.yaml"))
    if not yaml_files:
        print(f"(no .yaml files in {SOURCE})", file=sys.stderr)
        return 0

    for path in yaml_files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            print(f"✗ {path.name}: top-level must be a YAML list", file=sys.stderr)
            return 1
        scenarios = [transform_scenario(sc) for sc in data]
        out_path = OUT / f"{path.stem}.json"
        out_path.write_text(json.dumps(scenarios, indent=2) + "\n", encoding="utf-8")
        print(f"  · {path.name} → ECI.TestHarness/scenarios/{out_path.name} "
              f"({len(scenarios)} scenarios)")

    print(f"✓ Built {len(yaml_files)} scenario file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
