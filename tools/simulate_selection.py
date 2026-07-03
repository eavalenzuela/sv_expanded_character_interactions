#!/usr/bin/env python3
"""Stardew dialogue-key selection simulator.

Predicts which dialogue key Stardew would pick for a given NPC and
context, and which text the player would see, accounting for our
Content Patcher overrides.

Use this to verify intent *before* launching the game:
- Are we targeting a key that vanilla actually picks under these conditions?
- Does a more-specific vanilla key shadow our override?
- Does our When clause logically match the context we want?

This models the documented main paths of Stardew's daily-dialogue
selection algorithm (see https://stardewvalleywiki.com/Modding:Dialogue).
It is *not* a complete reimplementation — it explicitly does not handle
marriage dialogue, festival-day overrides, Resort_*, mail responses,
quest dialogue, or the year-based rotation suffixes (Mon_2, Mon_3).
Cases it doesn't model are flagged so you know when the simulator
output isn't authoritative.

Usage:
    # Single query
    python3 tools/simulate_selection.py \\
        --npc Linus --season spring --day 5 --weekday Fri \\
        --hearts 0 --location Mountain --weather Sun

    # Scenarios file
    python3 tools/simulate_selection.py --scenarios tools/test_scenarios.yaml

    # Cross-check every authored line against its intended context
    python3 tools/simulate_selection.py --check-yaml
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parent.parent
BASELINE = REPO / "harvest" / "baseline_dialogue"
INCLUDE = REPO / "ECI.Content" / "include"
I18N_DEFAULT = REPO / "ECI.Content" / "i18n" / "default.json"
SOURCE = REPO / "source" / "dialogue"


# ---------- context ----------

@dataclass
class Context:
    npc: str
    season: str = "spring"          # spring | summer | fall | winter
    day: int = 1                    # 1..28
    weekday: str = "Mon"            # Mon..Sun
    weather: str = "Sun"            # Sun | Rain | Storm | Snow | Wind | GreenRain
    location: str = "Town"          # internal map name (Mountain, Forest, LeahHouse, ...)
    hearts: int = 0                 # 0..14
    is_outdoors: bool = True
    is_met: bool = True             # False = first encounter; Stardew plays Introduction
    has_seen_events: list[int] = field(default_factory=list)
    has_flags: list[str] = field(default_factory=list)
    eci_player_did_today: list[str] = field(default_factory=list)
    eci_time_of_day_bucket: str = "morning"  # morning | midday | evening | late
    affinity: dict = field(default_factory=dict)  # {npc: {axis: int}}; missing = 0

    def heart_rung(self) -> int:
        """Returns the largest even heart-level <= hearts (0,2,4,6,8,10,12,14)."""
        return max(0, (self.hearts // 2) * 2)


WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ---------- key candidate generation ----------

def candidate_keys(ctx: Context) -> list[str]:
    """Returns dialogue keys to try, in priority order (highest first).

    Mirrors the documented selection order. Each key is just a candidate;
    the actual pick is the first one that exists in the data dict.
    """
    keys: list[str] = []

    # Location-specific (highest priority for ambient daily talk).
    keys.append(f"{ctx.location}_{ctx.weather}")
    keys.append(ctx.location)

    # Date-specific.
    keys.append(f"{ctx.season}_{ctx.day}")
    keys.append(str(ctx.day))

    # Season + weekday with heart-gating (highest hearts first).
    for h in (14, 12, 10, 8, 6, 4, 2):
        if ctx.heart_rung() >= h:
            keys.append(f"{ctx.season}_{ctx.weekday}{h}")
            keys.append(f"{ctx.season}_{ctx.weekday}_{h}")
    keys.append(f"{ctx.season}_{ctx.weekday}")

    # Weekday with heart-gating.
    for h in (14, 12, 10, 8, 6, 4, 2):
        if ctx.heart_rung() >= h:
            keys.append(f"{ctx.weekday}{h}")
            keys.append(f"{ctx.weekday}_{h}")
    keys.append(ctx.weekday)

    return keys


# ---------- override loading ----------

@dataclass
class Override:
    npc: str
    key: str
    text: str
    when: dict[str, str]
    log_name: str
    update: str = ""


def parse_target(target: str) -> str | None:
    """Returns the NPC name from a CP Target like 'Characters/Dialogue/Linus'."""
    parts = target.split("/")
    if len(parts) == 3 and parts[0] == "Characters" and parts[1] == "Dialogue":
        return parts[2]
    return None


I18N_REF_RE = re.compile(r"\{\{i18n:([^}]+)\}\}")


def load_i18n() -> dict[str, str]:
    """Translation strings emitted by build_cp.py (empty if built --no-i18n)."""
    if not I18N_DEFAULT.exists():
        return {}
    try:
        data = json.loads(I18N_DEFAULT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_i18n(text: str, i18n: dict[str, str]) -> str:
    """Replace {{i18n:key}} refs the way CP would, so text assertions in
    scenarios keep working against i18n-built fragments."""
    return I18N_REF_RE.sub(
        lambda m: i18n.get(m.group(1), m.group(0)), text)


def load_overrides() -> dict[str, list[Override]]:
    """Returns {npc: [Override, ...]} parsed from the built CP fragments."""
    out: dict[str, list[Override]] = {}
    if not INCLUDE.exists():
        return out
    i18n = load_i18n()
    for path in sorted(INCLUDE.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for change in data.get("Changes", []):
            if change.get("Action") != "EditData":
                continue
            target = change.get("Target", "")
            npc = parse_target(target)
            if npc is None:
                continue
            entries = change.get("Entries", {})
            when = change.get("When", {}) or {}
            log_name = change.get("LogName", "")
            update = change.get("Update", "")
            for key, text in entries.items():
                out.setdefault(npc, []).append(
                    Override(npc, key, resolve_i18n(text, i18n), when,
                             log_name, update)
                )
    return out


def load_vanilla(npc: str) -> dict[str, str]:
    path = BASELINE / f"{npc}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


# ---------- conditions matcher ----------

# Tokens we model. Anything outside this list is treated as "unknown" and
# its presence in a When clause causes the override to be reported as
# "unmodelable" rather than matched/unmatched.
KNOWN_TOKENS = {
    "Weather", "Season", "DayOfWeek", "Day", "LocationName",
    "LocationContext", "LocationUniqueName", "IsOutdoors",
    "Hearts",  # special: "Hearts": "Linus:4" form
    "eavalenzuela.ECI.Tokens/PlayerDidToday",
    "eavalenzuela.ECI.Tokens/TimeOfDayBucket",
}


def token_value(name: str, ctx: Context) -> Any:
    if name == "Weather":
        return ctx.weather
    if name == "Season":
        return ctx.season.capitalize()  # CP returns Spring not spring
    if name == "DayOfWeek":
        return {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
                "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday",
                "Sun": "Sunday"}[ctx.weekday]
    if name == "Day":
        return str(ctx.day)
    if name in ("LocationName", "LocationUniqueName"):
        return ctx.location
    if name == "IsOutdoors":
        return "true" if ctx.is_outdoors else "false"
    if name == "eavalenzuela.ECI.Tokens/PlayerDidToday":
        return list(ctx.eci_player_did_today)
    if name == "eavalenzuela.ECI.Tokens/TimeOfDayBucket":
        return ctx.eci_time_of_day_bucket
    return None  # unknown


@dataclass
class ConditionResult:
    matched: bool
    failed_tokens: list[str] = field(default_factory=list)
    unmodelable_tokens: list[str] = field(default_factory=list)


# Affinity Query keys as emitted by build_cp.affinity_to_query_when:
#   "Query: {{eavalenzuela.ECI.Tokens/Affinity<NPC><Axis>}} <op> <N>"
# The NPC/axis names are concatenated without a separator, so we split on
# the known axis suffixes (keep in sync with ECI.Tokens/ModEntry.cs).
AFFINITY_AXES = ("Trust", "Respect", "Romance")
AFFINITY_QUERY_RE = re.compile(
    r"^Query:\s*\{\{eavalenzuela\.ECI\.Tokens/Affinity([A-Za-z]+?)"
    r"(" + "|".join(AFFINITY_AXES) + r")\}\}\s*(>=|<=|<>|=|>|<)\s*(-?\d+)\s*$"
)

_QUERY_OPS = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    "=": lambda a, b: a == b,
    "<>": lambda a, b: a != b,
}


def evaluate_affinity_query(token_name: str, expected: str,
                            ctx: Context) -> bool | None:
    """Evaluate a build_cp-emitted affinity Query key against ctx.affinity.
    Returns True/False when modelable, None when this isn't an affinity
    Query (caller treats it as unmodelable)."""
    m = AFFINITY_QUERY_RE.match(token_name)
    if not m:
        return None
    npc, axis, op, val = m.group(1), m.group(2), m.group(3), int(m.group(4))
    actual = int(ctx.affinity.get(npc, {}).get(axis, 0))
    result = _QUERY_OPS[op](actual, val)
    # CP compares the Query result against the When value ("true"/"false").
    expect_true = str(expected).strip().lower() != "false"
    return result == expect_true


def evaluate_conditions(when: dict[str, str], ctx: Context) -> ConditionResult:
    if not when:
        return ConditionResult(matched=True)

    failed: list[str] = []
    unmodelable: list[str] = []

    for token_name, expected in when.items():
        if token_name not in KNOWN_TOKENS:
            affinity_match = evaluate_affinity_query(token_name, expected, ctx)
            if affinity_match is None:
                unmodelable.append(token_name)
            elif not affinity_match:
                failed.append(token_name)
            continue
        actual = token_value(token_name, ctx)
        # CP semantics: comma-separated value list = any-of
        expected_values = [v.strip() for v in str(expected).split(",")]
        if isinstance(actual, list):
            if not any(e.lower() == av.lower()
                       for e in expected_values for av in actual):
                failed.append(token_name)
        else:
            if not any(e.lower() == str(actual).lower() for e in expected_values):
                failed.append(token_name)

    if unmodelable:
        return ConditionResult(matched=False, unmodelable_tokens=unmodelable)
    return ConditionResult(matched=not failed, failed_tokens=failed)


# ---------- main predict ----------

@dataclass
class Pick:
    key: str | None
    text: str | None
    source: str             # "override" | "vanilla" | "none"
    log_name: str = ""
    skipped_overrides: list[tuple[Override, ConditionResult]] = field(default_factory=list)


def predict(ctx: Context, vanilla: dict[str, str], overrides: list[Override]) -> Pick:
    """For each candidate key (highest priority first):
       1. Find all overrides at that key whose When matches.
       2. The LAST one in load order wins (CP applies EditData patches in
          load order; later writes overwrite earlier ones).
       3. If no override matches, fall through to vanilla.

    Special case: if the player has not yet met this NPC (`is_met=False`)
    and an Introduction key exists, Stardew plays it instead of any
    weekday/season/location key. Caught the hard way during MVP testing.
    """
    by_key: dict[str, list[Override]] = {}
    for o in overrides:
        by_key.setdefault(o.key, []).append(o)

    skipped: list[tuple[Override, ConditionResult]] = []

    # Introduction takes precedence on first meeting.
    if not ctx.is_met and "Introduction" in vanilla:
        intro_overrides = by_key.get("Introduction", [])
        for o in intro_overrides:
            cr = evaluate_conditions(o.when, ctx)
            if cr.matched:
                return Pick("Introduction", o.text, "override", o.log_name, skipped)
            skipped.append((o, cr))
        return Pick("Introduction", vanilla["Introduction"], "vanilla", "", skipped)

    for key in candidate_keys(ctx):
        matching: list[Override] = []
        for o in by_key.get(key, []):
            cr = evaluate_conditions(o.when, ctx)
            if cr.matched:
                matching.append(o)
            else:
                skipped.append((o, cr))
        if matching:
            winner = matching[-1]
            return Pick(key, winner.text, "override", winner.log_name, skipped)
        if key in vanilla:
            return Pick(key, vanilla[key], "vanilla", "", skipped)

    return Pick(None, None, "none", "", skipped)


# ---------- printing ----------

def render_pick(ctx: Context, pick: Pick) -> str:
    out: list[str] = []
    affinity_note = f" affinity={ctx.affinity}" if ctx.affinity else ""
    out.append(f"{ctx.npc} | {ctx.season} {ctx.day} ({ctx.weekday}) | "
               f"loc={ctx.location} weather={ctx.weather} hearts={ctx.hearts} "
               f"timeBucket={ctx.eci_time_of_day_bucket} did={ctx.eci_player_did_today}"
               f"{affinity_note}")
    if pick.key is None:
        out.append("  → no matching key (NPC silent)")
    else:
        tag = pick.source.upper()
        suffix = f" [{pick.log_name}]" if pick.log_name else ""
        out.append(f"  → key={pick.key}  source={tag}{suffix}")
        text = (pick.text or "")[:140]
        out.append(f"    text: {text}{'…' if pick.text and len(pick.text) > 140 else ''}")
    if pick.skipped_overrides:
        out.append("  Skipped overrides on the way:")
        for o, cr in pick.skipped_overrides:
            reason = (
                f"failed: {cr.failed_tokens}"
                if cr.failed_tokens else
                f"unmodelable: {cr.unmodelable_tokens}"
            )
            out.append(f"    - {o.log_name} (key={o.key}) — {reason}")
    return "\n".join(out)


# ---------- CLI ----------

def parse_affinity_args(pairs: list[str] | None) -> dict[str, dict[str, int]]:
    """Parses repeatable --affinity args like 'Leah.Trust=5'."""
    out: dict[str, dict[str, int]] = {}
    for pair in pairs or []:
        m = re.match(r"^(\w+)\.(\w+)=(-?\d+)$", pair)
        if not m:
            raise SystemExit(
                f"✗ Bad --affinity {pair!r}; expected <NPC>.<Axis>=<int> "
                f"(e.g. Leah.Trust=5)")
        out.setdefault(m.group(1), {})[m.group(2)] = int(m.group(3))
    return out


def cli_single(args: argparse.Namespace) -> int:
    ctx = Context(
        npc=args.npc,
        season=args.season,
        day=args.day,
        weekday=args.weekday,
        weather=args.weather,
        location=args.location,
        hearts=args.hearts,
        is_met=not args.unmet,
        eci_time_of_day_bucket=args.time_bucket,
        eci_player_did_today=list(args.did or []),
        affinity=parse_affinity_args(args.affinity),
    )
    vanilla = load_vanilla(args.npc)
    if not vanilla:
        print(f"✗ No vanilla baseline for '{args.npc}' at {BASELINE}/{args.npc}.json",
              file=sys.stderr)
        return 1
    overrides = load_overrides().get(args.npc, [])
    pick = predict(ctx, vanilla, overrides)
    print(render_pick(ctx, pick))
    return 0


def cli_scenarios(path: Path) -> int:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        print(f"✗ {path} top-level must be a YAML list of scenarios", file=sys.stderr)
        return 1

    overrides_by_npc = load_overrides()
    fail = 0
    for i, sc in enumerate(raw, 1):
        ctx_args = sc.get("context", {})
        ctx = Context(
            npc=sc["npc"],
            season=ctx_args.get("season", "spring"),
            day=ctx_args.get("day", 1),
            weekday=ctx_args.get("weekday", "Mon"),
            weather=ctx_args.get("weather", "Sun"),
            location=ctx_args.get("location", "Town"),
            hearts=ctx_args.get("hearts", 0),
            is_met=ctx_args.get("is_met", True),
            eci_time_of_day_bucket=ctx_args.get("time_bucket", "morning"),
            eci_player_did_today=list(ctx_args.get("did", [])),
            affinity=dict(ctx_args.get("affinity", {})),
        )
        vanilla = load_vanilla(ctx.npc)
        overrides = overrides_by_npc.get(ctx.npc, [])
        pick = predict(ctx, vanilla, overrides)

        name = sc.get("name", f"scenario {i}")
        expect_source = sc.get("expect_source")     # "override" | "vanilla"
        expect_key = sc.get("expect_key")
        expect_log = sc.get("expect_log_name")
        expect_text_contains = sc.get("expect_text_contains")

        ok = True
        reasons: list[str] = []
        if expect_source and pick.source != expect_source:
            ok = False
            reasons.append(f"source={pick.source!r}, expected {expect_source!r}")
        if expect_key and pick.key != expect_key:
            ok = False
            reasons.append(f"key={pick.key!r}, expected {expect_key!r}")
        if expect_log and pick.log_name != expect_log:
            ok = False
            reasons.append(f"log_name={pick.log_name!r}, expected {expect_log!r}")
        if expect_text_contains and (pick.text or "").find(expect_text_contains) < 0:
            ok = False
            reasons.append(f"text doesn't contain {expect_text_contains!r}")

        if ok:
            print(f"✓ {name}")
        else:
            fail += 1
            print(f"✗ {name}")
            print("  " + "; ".join(reasons))
            print("  ↳ " + render_pick(ctx, pick).replace("\n", "\n    "))

    print()
    print(f"{len(raw) - fail}/{len(raw)} passed")
    return 1 if fail else 0


def cli_check_yaml() -> int:
    """Cross-check every line in source/dialogue/*.yaml against its intended
    context and confirm the override is reachable (i.e., is the picked key,
    not shadowed by a higher-priority vanilla key).

    Each YAML line should declare an `expect:` block (optional) of context
    values to test under. If absent, we skip — we don't try to guess intent.
    """
    overrides_by_npc = load_overrides()
    fail = 0
    checked = 0
    for path in sorted(SOURCE.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        npc = data["npc"]
        vanilla = load_vanilla(npc)
        overrides = overrides_by_npc.get(npc, [])
        for line in data.get("lines", []):
            expect = line.get("expect")
            if expect is None:
                continue
            ctx = Context(
                npc=npc,
                season=expect.get("season", "spring"),
                day=expect.get("day", 1),
                weekday=expect.get("weekday", "Mon"),
                weather=expect.get("weather", "Sun"),
                location=expect.get("location", "Town"),
                hearts=expect.get("hearts", 0),
                is_met=expect.get("is_met", True),
                eci_time_of_day_bucket=expect.get("time_bucket", "morning"),
                eci_player_did_today=list(expect.get("did", [])),
                affinity=dict(expect.get("affinity", {})),
            )
            checked += 1
            pick = predict(ctx, vanilla, overrides)
            if pick.source == "override" and pick.log_name.startswith(line["id"]):
                print(f"✓ {npc}/{line['id']}")
            else:
                fail += 1
                print(f"✗ {npc}/{line['id']}: expected our override to be picked, got "
                      f"source={pick.source}, key={pick.key}, log={pick.log_name}")
    print()
    print(f"{checked - fail}/{checked} authored lines reach their intended context")
    return 1 if fail else 0


def main() -> int:
    p = argparse.ArgumentParser(description="Stardew dialogue-key selection simulator")
    p.add_argument("--scenarios", type=Path,
                   help="YAML file with a list of scenarios to run")
    p.add_argument("--check-yaml", action="store_true",
                   help="Cross-check authored YAML lines against their `expect:` blocks")

    p.add_argument("--npc")
    p.add_argument("--season", default="spring",
                   choices=["spring", "summer", "fall", "winter"])
    p.add_argument("--day", type=int, default=1)
    p.add_argument("--weekday", default="Mon", choices=WEEKDAYS)
    p.add_argument("--weather", default="Sun")
    p.add_argument("--location", default="Town")
    p.add_argument("--hearts", type=int, default=0)
    p.add_argument("--time-bucket", default="morning",
                   choices=["morning", "midday", "evening", "late"])
    p.add_argument("--did", action="append",
                   help="A flag to add to ECI.PlayerDidToday (repeatable).")
    p.add_argument("--affinity", action="append",
                   help="Affinity value as <NPC>.<Axis>=<int>, e.g. "
                        "Leah.Trust=5 (repeatable).")
    p.add_argument("--unmet", action="store_true",
                   help="Simulate first-encounter (NPC has not been met yet — "
                        "Stardew plays Introduction first).")
    args = p.parse_args()

    if args.scenarios:
        return cli_scenarios(args.scenarios)
    if args.check_yaml:
        return cli_check_yaml()
    if not args.npc:
        p.error("specify --npc, --scenarios, or --check-yaml")
    return cli_single(args)


if __name__ == "__main__":
    sys.exit(main())
