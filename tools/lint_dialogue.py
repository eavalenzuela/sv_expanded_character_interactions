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
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Patterns Stardew's dialogue-selection algorithm actually probes. A
# target_key matching any of these is valid even if absent from vanilla:
# CP just adds it, and Stardew will pick it under matching context.
SEASONS = "spring|summer|fall|winter"
WEEKDAYS_RE = "Mon|Tue|Wed|Thu|Fri|Sat|Sun"
DIALOGUE_KEY_PATTERNS = [
    re.compile(rf"^({WEEKDAYS_RE})\d*$"),                       # Mon, Mon4
    re.compile(rf"^({SEASONS})_({WEEKDAYS_RE})\d*$"),           # spring_Mon, summer_Fri4
    re.compile(rf"^({SEASONS})_\d+$"),                          # spring_5
    re.compile(r"^\d+$"),                                       # 5 (day of month)
    re.compile(r"^Introduction$"),
    re.compile(r"^MovieInvitation$"),
    re.compile(r"^Resort.*$"),
    re.compile(r"^GreenRain.*$"),
    re.compile(r"^Marriage.*$"),
    re.compile(r"^married(_.*)?$"),
    re.compile(r"^dating(_.*)?$"),
    re.compile(rf"^Beach$|^Mountain$|^Town$|^Forest$|^Desert$|^Saloon$"),
    re.compile(rf"^({SEASONS})$"),                              # plain season
]


def looks_like_dialogue_key(key: str) -> bool:
    return any(p.match(key) for p in DIALOGUE_KEY_PATTERNS)

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

# Legal values for our custom tokens. A typo here (e.g. `chopedTree`)
# builds fine and then silently never fires in-game, so it's an error.
# Keep in sync with ECI.Tokens/ModEntry.cs (GetPlayerDidToday flags and
# GetTimeOfDayBucket buckets).
ECI_TOKEN_VALUES = {
    "eavalenzuela.ECI.Tokens/PlayerDidToday": {
        "gaveGift", "caughtFish", "choppedTree", "passedOut", "enteredMine",
        "visitedBeach", "visitedTown", "visitedSaloon",
    },
    "eavalenzuela.ECI.Tokens/TimeOfDayBucket": {
        "morning", "midday", "evening", "late",
    },
}

TIME_BUCKETS = {"morning", "midday", "evening", "late"}
SEASON_SET = {"spring", "summer", "fall", "winter"}

# Schema for the optional `expect:` block consumed by
# simulate_selection.py --check-yaml. key -> allowed type(s).
EXPECT_SCHEMA: dict[str, type | tuple[type, ...]] = {
    "season": str,
    "day": int,
    "weekday": str,
    "weather": str,
    "location": str,
    "hearts": int,
    "time_bucket": str,
    "did": list,
    "is_met": bool,
    "affinity": dict,
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


_vanilla_qid_cache: set[int] | None = None

_VANILLA_Q_RE = re.compile(r"\$q\s+(\d+)")


def vanilla_question_ids() -> set[int]:
    """Question ids used anywhere in the harvested vanilla dialogue.

    dialogueQuestionsAnswered is global player state, so an authored
    question id colliding with ANY vanilla `$q` id (not just the same
    NPC's) makes Stardew treat the question as already answered.
    Returns an empty set when nothing is harvested.
    """
    global _vanilla_qid_cache
    if _vanilla_qid_cache is not None:
        return _vanilla_qid_cache
    ids: set[int] = set()
    if BASELINE.exists():
        for path in BASELINE.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for text in data.values():
                for m in _VANILLA_Q_RE.finditer(str(text)):
                    ids.add(int(m.group(1)))
    _vanilla_qid_cache = ids
    return ids


# ---------- line-level checks ----------

def lint_line(line: Any, file: Path, npc: str, result: LintResult,
              seen_ids: dict[str, Path],
              seen_qids: dict[int, tuple[Path, str]],
              seen_rids: dict[str, tuple[Path, str]],
              authored_keys: set[str]) -> None:
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

    # text vs question — exactly one must be present
    has_text = isinstance(line.get("text"), str) and line["text"].strip() != ""
    has_question = isinstance(line.get("question"), dict)
    if has_text and has_question:
        result.add("error", file, line_id,
                   "line has both 'text' and 'question'; pick one (question replaces text)")
    elif not has_text and not has_question:
        result.add("error", file, line_id, "missing or empty 'text' (or 'question')")

    if has_question:
        q = line["question"]
        qid = q.get("id")
        if not isinstance(qid, int):
            result.add("error", file, line_id, "question.id must be an integer")
        else:
            if qid in seen_qids:
                prev_file, prev_line = seen_qids[qid]
                result.add("error", file, line_id,
                           f"duplicate question.id {qid} (also used by "
                           f"{prev_line} in {prev_file.name}) — Stardew tracks "
                           f"answered questions by this id globally")
            else:
                seen_qids[qid] = (file, line_id)
            if qid in vanilla_question_ids():
                result.add("warning", file, line_id,
                           f"question.id {qid} collides with a vanilla $q id — "
                           f"Stardew may treat it as already answered. Pick an "
                           f"id outside the vanilla range (e.g. 1600+).")
        if not isinstance(q.get("text"), str) or not q["text"].strip():
            result.add("error", file, line_id, "question.text missing or empty")
        # Fallback key: the literal "null" sentinel (also the default) or a
        # dialogue key that will actually exist — Stardew does a direct
        # speaker.Dialogue[fallback] lookup and throws KeyNotFound otherwise.
        fallback = q.get("fallback")
        if fallback is not None and fallback != "null":
            if not isinstance(fallback, str) or not fallback.strip():
                result.add("error", file, line_id,
                           "question.fallback must be the string 'null' or a "
                           "dialogue key")
            else:
                baseline = baseline_keys_for(npc) or set()
                if fallback not in baseline and fallback not in authored_keys:
                    result.add("error", file, line_id,
                               f"question.fallback {fallback!r} is neither a "
                               f"vanilla {npc} dialogue key nor authored in this "
                               f"file — Stardew throws KeyNotFound on the second "
                               f"talk. Use 'null' to skip the fallback lookup.")
        responses = q.get("responses")
        if not isinstance(responses, list) or len(responses) < 2:
            result.add("error", file, line_id,
                       "question.responses must be a list of ≥2 entries")
        else:
            for r in responses:
                if not isinstance(r, dict):
                    result.add("error", file, line_id, f"response is not a mapping: {r!r}")
                    continue
                rid = r.get("id")
                if not isinstance(rid, str) or not rid.strip():
                    result.add("error", file, line_id, "response.id missing or not a string")
                elif rid in seen_rids:
                    prev_file, prev_line = seen_rids[rid]
                    result.add("error", file, line_id,
                               f"duplicate response id {rid!r} (also used by "
                               f"{prev_line} in {prev_file.name}) — response ids "
                               f"must be globally unique")
                else:
                    seen_rids[rid] = (file, line_id)
                if not isinstance(r.get("text"), str) or not r["text"].strip():
                    result.add("error", file, line_id, f"response {r.get('id')!r} text missing or empty")
                if not isinstance(r.get("followup"), str) or not r["followup"].strip():
                    result.add("warning", file, line_id,
                               f"response {r.get('id')!r} has no 'followup' — "
                               f"players will see the '...' placeholder after "
                               f"picking it")
                friendship = r.get("friendship")
                if friendship is not None and not isinstance(friendship, int):
                    result.add("error", file, line_id,
                               f"response {r.get('id')!r} friendship must be int, "
                               f"got {type(friendship).__name__}")
                affinity = r.get("affinity")
                if affinity is not None and not isinstance(affinity, dict):
                    result.add("error", file, line_id,
                               f"response {r.get('id')!r} affinity must be a mapping")
                elif isinstance(affinity, dict):
                    for npc_name, axes in affinity.items():
                        if not isinstance(axes, dict):
                            result.add("error", file, line_id,
                                       f"response {r.get('id')!r} affinity.{npc_name} must be a mapping")
                            continue
                        for axis, delta in axes.items():
                            if not isinstance(delta, int):
                                result.add("error", file, line_id,
                                           f"response {r.get('id')!r} affinity.{npc_name}.{axis} must be int, got {type(delta).__name__}")

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

    # Validate that resolved target keys exist in vanilla OR look like a
    # known Stardew dialogue key pattern. Adding a new entry that matches
    # Stardew's selection patterns is valid (CP extends the dict), so we
    # only warn when the target looks like it could be a typo.
    baseline = baseline_keys_for(npc)
    if baseline is not None:
        resolved: list[str] = []
        for t in targets:
            if t == "*":
                resolved.extend(WEEKDAYS)
            elif t == "any_day":
                # 7 plain + 7×3 season-prefixed; mirrors build_cp.any_day_keys()
                resolved.extend(WEEKDAYS)
                for season in ("summer", "fall", "winter"):
                    resolved.extend(f"{season}_{w}" for w in WEEKDAYS)
            else:
                resolved.append(t)
        suspicious = [
            k for k in resolved
            if k not in baseline and not looks_like_dialogue_key(k)
        ]
        if suspicious:
            result.add(
                "warning", file, line_id,
                f"target_key(s) {sorted(set(suspicious))} are neither in vanilla "
                f"{npc}.json nor a recognized Stardew dialogue key pattern — possible typo.")

    # If a line has When LocationName=X and vanilla has a key named X,
    # Stardew will pick the `X` key BEFORE weekday selection — so our
    # weekday-targeted override never fires there. Must target the
    # location-key directly.
    if isinstance(when := line.get("when"), dict):
        loc = when.get("LocationName")
        if isinstance(loc, str) and baseline is not None and loc in baseline:
            targets_match_loc_key = (
                isinstance(target, str) and target == loc
            ) or (isinstance(target, list) and loc in target)
            if not targets_match_loc_key:
                result.add(
                    "warning", file, line_id,
                    f"vanilla {npc}.json has a `{loc}` location-key which "
                    f"Stardew picks before weekday keys — to override at this "
                    f"location, set target_key: {loc} (not weekday keys).")

    # affinity block inside When (translated to Query at build time)
    if isinstance(when := line.get("when"), dict) and "affinity" in when:
        aff = when["affinity"]
        if not isinstance(aff, dict):
            result.add("error", file, line_id, "when.affinity must be a mapping")
        else:
            for npc_name, axes in aff.items():
                if not isinstance(axes, dict):
                    result.add("error", file, line_id,
                               f"when.affinity.{npc_name} must be a mapping")
                    continue
                # These names become part of the Affinity<NPC><Axis> CP
                # token, and CP silently rejects token names containing
                # anything but letters.
                if not re.fullmatch(r"[A-Za-z]+", str(npc_name)):
                    result.add(
                        "error", file, line_id,
                        f"when.affinity NPC name {npc_name!r} must be letters "
                        f"only — it becomes part of a CP token name.")
                for axis, expr in axes.items():
                    if not re.fullmatch(r"[A-Za-z]+", str(axis)):
                        result.add(
                            "error", file, line_id,
                            f"when.affinity axis {axis!r} must be letters only "
                            f"— it becomes part of a CP token name.")
                    if not isinstance(expr, str) or not re.match(
                        r"^\s*(>=|<=|!=|==|=|>|<)\s*-?\d+\s*$", expr
                    ):
                        result.add(
                            "error", file, line_id,
                            f"when.affinity.{npc_name}.{axis} must be a string "
                            f"like '>=5', '<3', '=0', '!=10', got {expr!r}")

    # when block
    when = line.get("when")
    if when is not None:
        if not isinstance(when, dict):
            result.add("error", file, line_id, "'when' must be a mapping")
        else:
            for k, v in when.items():
                if k == "affinity":
                    continue  # handled above
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

                # Token-VALUE check for our own tokens. CP treats a
                # comma-separated value as any-of; validate each element.
                if k in ECI_TOKEN_VALUES and isinstance(v, str):
                    legal = ECI_TOKEN_VALUES[k]
                    bad = [part for part in (p.strip() for p in v.split(","))
                           if part and part not in legal]
                    if bad:
                        result.add(
                            "error", file, line_id,
                            f"unknown value(s) {bad} for token '{k}' — the line "
                            f"would never fire. Legal values: {sorted(legal)}.")

    # expect block (optional; consumed by simulate_selection.py --check-yaml)
    expect = line.get("expect")
    if expect is not None:
        if not isinstance(expect, dict):
            result.add("error", file, line_id, "'expect' must be a mapping")
        else:
            for k, v in expect.items():
                if k not in EXPECT_SCHEMA:
                    result.add("error", file, line_id,
                               f"unknown expect key {k!r} — allowed: "
                               f"{sorted(EXPECT_SCHEMA)}")
                    continue
                if not isinstance(v, EXPECT_SCHEMA[k]):
                    result.add("error", file, line_id,
                               f"expect.{k} must be "
                               f"{EXPECT_SCHEMA[k].__name__}, got "
                               f"{type(v).__name__}")
                    continue
                if k == "season" and v not in SEASON_SET:
                    result.add("error", file, line_id,
                               f"expect.season {v!r} not in {sorted(SEASON_SET)}")
                elif k == "weekday" and v not in WEEKDAYS:
                    result.add("error", file, line_id,
                               f"expect.weekday {v!r} not in {sorted(WEEKDAYS)}")
                elif k == "time_bucket" and v not in TIME_BUCKETS:
                    result.add("error", file, line_id,
                               f"expect.time_bucket {v!r} not in {sorted(TIME_BUCKETS)}")
                elif k == "did":
                    legal = ECI_TOKEN_VALUES["eavalenzuela.ECI.Tokens/PlayerDidToday"]
                    bad = [f for f in v if f not in legal]
                    if bad:
                        result.add("error", file, line_id,
                                   f"expect.did has unknown flag(s) {bad} — "
                                   f"legal: {sorted(legal)}")
                elif k == "affinity":
                    for npc_name, axes in v.items():
                        if not isinstance(axes, dict) or not all(
                            isinstance(val, int) for val in axes.values()
                        ):
                            result.add("error", file, line_id,
                                       f"expect.affinity.{npc_name} must map "
                                       f"axis → int")


# ---------- file-level + cross-file checks ----------

def authored_keys_for(lines: list[Any]) -> set[str]:
    """All dialogue-dict keys this file will emit: expanded target keys
    plus response ids (each response gets a followup entry)."""
    keys: set[str] = set()
    for line in lines:
        if not isinstance(line, dict):
            continue
        target = line.get("target_key", "*")
        targets = [target] if isinstance(target, str) else (
            list(target) if isinstance(target, list) else [])
        for t in targets:
            if t == "*":
                keys.update(WEEKDAYS)
            elif t == "any_day":
                keys.update(WEEKDAYS)
                for season in ("summer", "fall", "winter"):
                    keys.update(f"{season}_{w}" for w in WEEKDAYS)
            elif isinstance(t, str):
                keys.add(t)
        question = line.get("question")
        if isinstance(question, dict):
            for r in question.get("responses") or []:
                if isinstance(r, dict) and isinstance(r.get("id"), str):
                    keys.add(r["id"])
    return keys


def lint_file(file: Path, result: LintResult, seen_ids: dict[str, Path],
              seen_qids: dict[int, tuple[Path, str]],
              seen_rids: dict[str, tuple[Path, str]]) -> None:
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

    authored_keys = authored_keys_for(lines)
    for line in lines:
        lint_line(line, file, npc, result, seen_ids, seen_qids, seen_rids,
                  authored_keys)


def lint_all(yaml_files: list[Path]) -> LintResult:
    result = LintResult()
    seen_ids: dict[str, Path] = {}
    seen_qids: dict[int, tuple[Path, str]] = {}
    seen_rids: dict[str, tuple[Path, str]] = {}
    for f in yaml_files:
        lint_file(f, result, seen_ids, seen_qids, seen_rids)
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
