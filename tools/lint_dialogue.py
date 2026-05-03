#!/usr/bin/env python3
"""Static linter for source/dialogue/*.yaml authoring files.

Catches the bug classes we hit during MVP smoke testing without launching
the game:

  - Missing/wrong field types in the YAML schema
  - target_key that doesn't exist in the NPC's vanilla dialogue file
    (these would silently never fire — the issue we hit with `spring_Thu`)
  - NPC name not present in harvested baseline (typos)
  - Duplicate line ids across all YAMLs
  - Token names that aren't recognized CP built-ins or namespaced custom
    tokens (catches typos like `LociationName` or `Wether`)
  - Empty text strings
  - When-block keys/values that aren't strings

Usage: imported and called by build_cp.py, or run standalone:
    python3 tools/lint_dialogue.py
Returns exit code 1 on any error; warnings only print.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "source" / "dialogue"
BASELINE = REPO / "harvest" / "baseline_dialogue"

WEEKDAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}

# Content Patcher 2.x built-in tokens. Source: docs/author-tokens-guide.md
CP_BUILTIN_TOKENS = {
    # Player / save
    "ChildGenders", "ChildNames", "DailyLuck", "FarmCave", "FarmhouseUpgrade",
    "FarmMapAsset", "FarmName", "FarmType", "HasActiveQuest", "HasCaughtFish",
    "HasConversationTopic", "HasCookingRecipe", "HasCraftingRecipe",
    "HasDialogueAnswer", "HasFlag", "HasMod", "HasProfession", "HasReadLetter",
    "HasSeenEvent", "HasValue", "HasVisitedLocation", "HasWalletItem",
    "HavingChild", "Hearts", "IsCommunityCenterComplete",
    "IsJojaMartComplete", "IsMainPlayer", "PlayerGender", "PlayerName",
    "PreferredPet", "Pregnant", "Relationship", "Roommate", "SkillLevel",
    "Spouse",
    # World
    "Day", "DayEvent", "DayOfWeek", "DaysPlayed", "IsOutdoors",
    "Language", "LocationContext", "LocationName", "LocationOwnerId",
    "LocationUniqueName", "Season", "Time", "Weather", "Year",
    # Patch utility
    "Count", "FormatAssetName", "Lowercase", "Merge", "PathPart", "Query",
    "Random", "Range", "Render", "Round", "Uppercase",
    # Local CP
    "ModId",
}

# Tokens we register ourselves. Keep in sync with ECI.Tokens/ModEntry.cs.
ECI_TOKENS = {
    "eavalenzuela.ECI.Tokens/PlayerDidToday",
    "eavalenzuela.ECI.Tokens/TimeOfDayBucket",
}

# Tokens whose presence in a When block requires a non-default Update mode
# (set automatically by build_cp.py, but linted in case authors override).
LOCATION_TOKENS = {"LocationName", "LocationContext", "LocationOwnerId",
                   "LocationUniqueName", "IsOutdoors"}
TIME_TOKENS = {"Time"}
DYNAMIC_CUSTOM_TOKENS = ECI_TOKENS  # all our tokens change mid-day


@dataclass
class Issue:
    severity: str          # "error" | "warning"
    file: Path
    line_id: str | None
    message: str

    def __str__(self) -> str:
        loc = f"{self.file.name}"
        if self.line_id:
            loc += f" :: {self.line_id}"
        prefix = "✗" if self.severity == "error" else "!"
        return f"{prefix} [{self.severity:7}] {loc}: {self.message}"


@dataclass
class LintResult:
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    def add(self, severity: str, file: Path, line_id: str | None, msg: str) -> None:
        self.issues.append(Issue(severity, file, line_id, msg))


# ---------- baseline lookup helpers ----------

_baseline_keys_cache: dict[str, set[str]] = {}


def baseline_keys_for(npc: str) -> set[str] | None:
    """Returns the set of keys present in the vanilla dialogue file for an NPC,
    or None if the NPC has no harvested baseline file."""
    if npc in _baseline_keys_cache:
        return _baseline_keys_cache[npc]
    path = BASELINE / f"{npc}.json"
    if not path.exists():
        _baseline_keys_cache[npc] = set()
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        keys = set(data.keys())
    except json.JSONDecodeError:
        keys = set()
    _baseline_keys_cache[npc] = keys
    return keys


# ---------- line-level checks ----------

def lint_line(line: Any, file: Path, npc: str, result: LintResult,
              seen_ids: dict[str, Path]) -> None:
    if not isinstance(line, dict):
        result.add("error", file, None, f"line is not a mapping: {line!r}")
        return

    line_id = line.get("id")
    if not line_id or not isinstance(line_id, str):
        result.add("error", file, None, "line missing string 'id'")
        return

    if line_id in seen_ids:
        prev = seen_ids[line_id]
        result.add("error", file, line_id,
                   f"duplicate id (also defined in {prev.name})")
    else:
        seen_ids[line_id] = file

    # text
    text = line.get("text")
    if not isinstance(text, str) or not text.strip():
        result.add("error", file, line_id, "missing or empty 'text'")

    # target_key
    target = line.get("target_key", "*")
    if isinstance(target, str):
        targets = [target]
    elif isinstance(target, list):
        targets = list(target)
    else:
        result.add("error", file, line_id,
                   f"'target_key' must be string or list, got {type(target).__name__}")
        targets = []

    # Validate that resolved target keys exist in the NPC's vanilla file.
    baseline = baseline_keys_for(npc)
    if baseline is not None:
        resolved: list[str] = []
        for t in targets:
            if t == "*":
                resolved.extend(WEEKDAYS)
            else:
                resolved.append(t)
        missing = [k for k in resolved if k not in baseline]
        if missing:
            result.add(
                "warning", file, line_id,
                f"target_key(s) not present in vanilla {npc}.json: {sorted(set(missing))} "
                f"— these patches will silently never fire.")

    # when block
    when = line.get("when")
    if when is not None:
        if not isinstance(when, dict):
            result.add("error", file, line_id, "'when' must be a mapping")
        else:
            for k, v in when.items():
                if not isinstance(k, str):
                    result.add("error", file, line_id,
                               f"when key {k!r} must be a string")
                    continue
                if not isinstance(v, (str, int, float, bool)):
                    result.add("error", file, line_id,
                               f"when value for {k!r} must be scalar, got {type(v).__name__}")

                # Token-name plausibility check.
                if "/" in k:
                    # Namespaced token (e.g., eavalenzuela.ECI.Tokens/PlayerDidToday).
                    if k not in ECI_TOKENS:
                        result.add(
                            "warning", file, line_id,
                            f"unknown namespaced token '{k}' — typo? "
                            f"(known ECI tokens: {sorted(ECI_TOKENS)})")
                else:
                    if k not in CP_BUILTIN_TOKENS:
                        result.add(
                            "warning", file, line_id,
                            f"unknown CP built-in token '{k}' — typo? "
                            f"If it's a custom mod token, namespace it as 'Author.Mod/Token'.")


# ---------- file-level + cross-file checks ----------

def lint_file(file: Path, result: LintResult, seen_ids: dict[str, Path]) -> None:
    try:
        raw = file.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        result.add("error", file, None, f"YAML parse error: {e}")
        return

    if not isinstance(data, dict):
        result.add("error", file, None, "top-level must be a mapping with 'npc' and 'lines'")
        return

    npc = data.get("npc")
    if not isinstance(npc, str) or not npc:
        result.add("error", file, None, "missing string 'npc' field")
        return

    if baseline_keys_for(npc) is None:
        result.add(
            "warning", file, None,
            f"NPC '{npc}' has no harvested baseline at {BASELINE}/{npc}.json — "
            f"target_key validation will be skipped. Run setup_harvest.sh, or check NPC name spelling.")

    lines = data.get("lines")
    if not isinstance(lines, list):
        result.add("error", file, None, "'lines' must be a list")
        return

    for line in lines:
        lint_line(line, file, npc, result, seen_ids)


def lint_all(yaml_files: list[Path]) -> LintResult:
    result = LintResult()
    seen_ids: dict[str, Path] = {}
    for f in yaml_files:
        lint_file(f, result, seen_ids)
    return result


# ---------- CLI ----------

def main() -> int:
    yaml_files = sorted(SOURCE.glob("*.yaml"))
    if not yaml_files:
        print(f"(no YAML files in {SOURCE})", file=sys.stderr)
        return 0

    result = lint_all(yaml_files)

    if not result.issues:
        print(f"✓ Lint clean — {len(yaml_files)} file(s)")
        return 0

    by_severity: defaultdict[str, list[Issue]] = defaultdict(list)
    for issue in result.issues:
        by_severity[issue.severity].append(issue)

    for issue in result.issues:
        print(issue, file=sys.stderr)

    print(file=sys.stderr)
    print(
        f"Lint: {len(result.errors)} error(s), {len(result.warnings)} warning(s)",
        file=sys.stderr,
    )
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
