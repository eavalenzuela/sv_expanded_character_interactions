#!/usr/bin/env python3
"""Build Content Patcher fragments from source/dialogue/*.yaml.

Reads YAML dialogue files, validates them, and emits:
- ECI.Content/include/<npc>.json   (per-NPC CP fragment)
- ECI.Content/content.json         (CP root that Includes the fragments)

The strategy: each YAML line becomes one or more CP `EditData` ops on
`Characters/Dialogue/<NPC>` that conditionally override a vanilla
weekday key (Mon, Tue, …) using a `When` block. When the conditions
don't match, the vanilla line stays in place.

Run: python3 tools/build_cp.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from lint_dialogue import lint_all

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "source" / "dialogue"
OUT = REPO / "ECI.Content"
INCLUDE = OUT / "include"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SEASONS = ["spring", "summer", "fall", "winter"]

CP_FORMAT = "2.0.0"


def any_day_keys() -> list[str]:
    """All weekday keys an NPC's daily-dialogue selection might land on:
    plain `Mon..Sun` (spring fallback) plus `<season>_<weekday>` for
    summer/fall/winter. 7 + 21 = 28 keys.

    Use when a line should fire on a context (e.g., a weather condition)
    that's independent of season or weekday.
    """
    keys = list(WEEKDAYS)
    for s in ("summer", "fall", "winter"):
        keys.extend(f"{s}_{w}" for w in WEEKDAYS)
    return keys


def expand_target_keys(target_key: Any) -> list[str]:
    if isinstance(target_key, str):
        if target_key == "*":
            return WEEKDAYS[:]
        if target_key == "any_day":
            return any_day_keys()
        return [target_key]
    if isinstance(target_key, list):
        out: list[str] = []
        for t in target_key:
            out.extend(expand_target_keys(t))
        return out
    raise ValueError(f"Bad target_key: {target_key!r}")


# ---------- emit ----------

def build_npc_fragment(npc: str, lines: list[dict]) -> dict:
    """Returns the body of a CP secondary file. No `Format` field — that's
    only allowed on the root content.json; secondary (Include'd) files must
    omit it.

    Every patch with a `When` block gets `Update: OnLocationChange,OnTimeChange`
    so CP re-evaluates conditions when the player moves or time advances.
    Without this, location-/time-/custom-token-conditioned patches would only
    re-check at day-start and effectively never fire mid-day.
    """
    changes: list[dict] = []
    for line in lines:
        line_id = line["id"]
        text = line["text"]
        when = line.get("when") or {}
        keys = expand_target_keys(line.get("target_key", "*"))
        for key in keys:
            change: dict[str, Any] = {
                "Action": "EditData",
                "Target": f"Characters/Dialogue/{npc}",
                "Entries": {key: text},
                "LogName": f"{line_id}/{key}",
            }
            if when:
                change["When"] = {str(k): str(v) for k, v in when.items()}
                change["Update"] = "OnLocationChange,OnTimeChange"
            changes.append(change)
    return {"Changes": changes}


def build_root(fragment_paths: list[str]) -> dict:
    return {
        "Format": CP_FORMAT,
        "Changes": [
            {"Action": "Include", "FromFile": f}
            for f in fragment_paths
        ],
    }


# ---------- main ----------

def main() -> int:
    if not SOURCE.exists():
        print(f"✗ {SOURCE} not found", file=sys.stderr)
        return 1

    INCLUDE.mkdir(parents=True, exist_ok=True)

    yaml_files = sorted(SOURCE.glob("*.yaml"))
    if not yaml_files:
        print(f"✗ No YAML files in {SOURCE}", file=sys.stderr)
        return 1

    # Lint pass — refuse to build on errors, print warnings.
    lint_result = lint_all(yaml_files)
    if lint_result.errors:
        print("Lint errors — aborting build:", file=sys.stderr)
        for issue in lint_result.errors:
            print(f"  {issue}", file=sys.stderr)
        return 1
    if lint_result.warnings:
        print(f"Lint warnings ({len(lint_result.warnings)}):", file=sys.stderr)
        for issue in lint_result.warnings:
            print(f"  {issue}", file=sys.stderr)
        print(file=sys.stderr)

    fragment_paths: list[str] = []
    total_lines = 0
    total_changes = 0

    for yaml_path in yaml_files:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        npc = data["npc"]
        lines = data["lines"]
        fragment = build_npc_fragment(npc, lines)
        out_path = INCLUDE / f"{npc.lower()}.json"
        out_path.write_text(json.dumps(fragment, indent=2) + "\n", encoding="utf-8")
        rel = out_path.relative_to(OUT).as_posix()
        fragment_paths.append(rel)
        total_lines += len(lines)
        total_changes += len(fragment["Changes"])
        print(f"  · {npc}: {len(lines)} lines → {len(fragment['Changes'])} CP changes → {rel}")

    root = build_root(fragment_paths)
    (OUT / "content.json").write_text(json.dumps(root, indent=2) + "\n", encoding="utf-8")

    print(f"✓ Built {total_lines} lines → {total_changes} CP changes across {len(fragment_paths)} fragment(s)")
    print(f"  Root: {OUT / 'content.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
