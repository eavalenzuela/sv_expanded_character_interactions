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

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "source" / "dialogue"
OUT = REPO / "ECI.Content"
INCLUDE = OUT / "include"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

CP_FORMAT = "2.0.0"


# ---------- validation ----------

def validate_line(line: dict[str, Any], yaml_path: Path) -> list[str]:
    errors: list[str] = []
    if "id" not in line:
        errors.append(f"{yaml_path}: line missing 'id'")
    if "text" not in line:
        errors.append(f"{yaml_path}: line {line.get('id', '?')} missing 'text'")
    when = line.get("when")
    if when is not None and not isinstance(when, dict):
        errors.append(f"{yaml_path}: line {line.get('id', '?')} 'when' must be a mapping")
    target = line.get("target_key", "*")
    if not isinstance(target, (str, list)):
        errors.append(f"{yaml_path}: line {line.get('id', '?')} bad 'target_key'")
    return errors


def expand_target_keys(target_key: Any) -> list[str]:
    if isinstance(target_key, str):
        return WEEKDAYS[:] if target_key == "*" else [target_key]
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

    all_errors: list[str] = []
    fragment_paths: list[str] = []
    total_lines = 0
    total_changes = 0

    for yaml_path in yaml_files:
        raw = yaml_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        if not isinstance(data, dict) or "npc" not in data or "lines" not in data:
            all_errors.append(f"{yaml_path}: missing 'npc' or 'lines'")
            continue

        npc = data["npc"]
        lines = data["lines"]
        if not isinstance(lines, list):
            all_errors.append(f"{yaml_path}: 'lines' must be a list")
            continue

        for line in lines:
            all_errors.extend(validate_line(line, yaml_path))

        if all_errors:
            continue

        fragment = build_npc_fragment(npc, lines)
        out_path = INCLUDE / f"{npc.lower()}.json"
        out_path.write_text(json.dumps(fragment, indent=2) + "\n", encoding="utf-8")
        rel = out_path.relative_to(OUT).as_posix()
        fragment_paths.append(rel)
        total_lines += len(lines)
        total_changes += len(fragment["Changes"])
        print(f"  · {npc}: {len(lines)} lines → {len(fragment['Changes'])} CP changes → {rel}")

    if all_errors:
        for e in all_errors:
            print(f"✗ {e}", file=sys.stderr)
        return 1

    root = build_root(fragment_paths)
    (OUT / "content.json").write_text(json.dumps(root, indent=2) + "\n", encoding="utf-8")

    print(f"✓ Built {total_lines} lines → {total_changes} CP changes across {len(fragment_paths)} fragment(s)")
    print(f"  Root: {OUT / 'content.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
