#!/usr/bin/env python3
"""Authored-line coverage report.

Sweeps realistic context combinations through the selection simulator
(simulate_selection.predict) and reports, per NPC:

  - how often our overrides vs. vanilla win (and how often the NPC would
    be silent),
  - per-line pick counts across the sweep,
  - DEAD lines: authored lines never picked in any swept context.

Dead lines are almost always a load-order casualty — CP applies EditData
patches in file order with last-write-wins per key, so an always-true
axis (time-of-day covers every moment; day-of-week covers its whole day)
shadows every earlier patch on the same key. This tool makes that
visible before anyone burns an evening testing in-game.

The sweep is deliberately coarse (one representative day per weekday,
season-legal weathers only, single recent-action flags) — it measures
reachability, not frequency. Query/affinity-gated lines are swept at
affinity 0 and at the gate values found in the authored YAML expects.

Usage:
    python3 tools/coverage_report.py                # all NPCs
    python3 tools/coverage_report.py --npc Leah     # one NPC
    python3 tools/coverage_report.py --fail-on-dead # exit 1 if dead lines
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

from simulate_selection import (
    Context,
    load_overrides,
    load_vanilla,
    predict,
)

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "source" / "dialogue"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TIME_BUCKETS = ["morning", "midday", "evening", "late"]

# Season-legal weathers (Stardew: no rain in winter, snow only in winter,
# green rain only in summer).
SEASON_WEATHERS = {
    "spring": ["Sun", "Rain", "Storm", "Wind"],
    "summer": ["Sun", "Rain", "Storm", "GreenRain"],
    "fall": ["Sun", "Rain", "Storm", "Wind"],
    "winter": ["Sun", "Snow", "Wind"],
}

# One neutral location (no override targets it) + every location our
# When clauses or location-keys reference, gathered per NPC at runtime.
NEUTRAL_LOCATION = "Backwoods"

DID_FLAGS = ["choppedTree", "caughtFish", "gaveGift", "enteredMine",
             "passedOut", "visitedBeach", "visitedTown", "visitedSaloon"]

# Dialogue-key shapes that are context keys rather than location keys.
_CONTEXT_KEY_RE = re.compile(
    r"^(?:(?:spring|summer|fall|winter)_)?(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\d*$"
    r"|^(?:spring|summer|fall|winter)_\d+$"
    r"|^\d+$"
    r"|^Introduction$"
)


def locations_for(overrides: list) -> list[str]:
    """Locations worth sweeping for this NPC: every LocationName referenced
    in a When clause, every non-context override key (location-keys like
    Beach/JojaMart), plus one neutral location."""
    locs: set[str] = {NEUTRAL_LOCATION}
    for o in overrides:
        loc = o.when.get("LocationName")
        if isinstance(loc, str):
            locs.update(part.strip() for part in loc.split(","))
        if not _CONTEXT_KEY_RE.match(o.key):
            locs.add(o.key)
    return sorted(locs)


def affinity_profiles(yaml_path: Path) -> list[dict]:
    """Affinity contexts to sweep: all-zero plus each distinct affinity
    dict found in the file's expect blocks (i.e., the authored gate
    values)."""
    profiles: list[dict] = [{}]
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    for line in data.get("lines", []):
        expect = line.get("expect") or {}
        aff = expect.get("affinity")
        if aff and aff not in profiles:
            profiles.append(aff)
    return profiles


def sweep_npc(npc: str, yaml_path: Path, overrides: list,
              vanilla: dict[str, str]) -> tuple[Counter, Counter, int]:
    """Returns (per-line pick counts, per-source counts, total contexts)."""
    line_picks: Counter = Counter()
    source_counts: Counter = Counter()
    total = 0

    locations = locations_for(overrides)
    profiles = affinity_profiles(yaml_path)
    did_options: list[list[str]] = [[]] + [[f] for f in DID_FLAGS]

    for season, weathers in SEASON_WEATHERS.items():
        for wd_index, weekday in enumerate(WEEKDAYS):
            day = 8 + wd_index  # week 2: dodges most vanilla date-keys
            for weather in weathers:
                for bucket in TIME_BUCKETS:
                    for location in locations:
                        for did in did_options:
                            for affinity in profiles:
                                total += 1
                                ctx = Context(
                                    npc=npc, season=season, day=day,
                                    weekday=weekday, weather=weather,
                                    location=location, hearts=0,
                                    eci_time_of_day_bucket=bucket,
                                    eci_player_did_today=list(did),
                                    affinity=affinity,
                                )
                                pick = predict(ctx, vanilla, overrides)
                                source_counts[pick.source] += 1
                                if pick.source == "override" and pick.log_name:
                                    line_id = pick.log_name.split("/", 1)[0]
                                    line_picks[line_id] += 1
    return line_picks, source_counts, total


def report_npc(yaml_path: Path, overrides_by_npc: dict) -> int:
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    npc = data["npc"]
    line_ids = [line["id"] for line in data.get("lines", [])]
    overrides = overrides_by_npc.get(npc, [])
    vanilla = load_vanilla(npc)

    if not overrides:
        print(f"\n=== {npc}: no built overrides (run build_cp.py first) ===")
        return 0

    line_picks, source_counts, total = sweep_npc(npc, yaml_path, overrides, vanilla)

    print(f"\n=== {npc} — {len(line_ids)} authored lines, "
          f"{total} swept contexts ===")
    for source in ("override", "vanilla", "none"):
        n = source_counts.get(source, 0)
        print(f"  {source:9} {n:7}  ({100 * n / total:5.1f}%)")

    dead = [lid for lid in line_ids if line_picks.get(lid, 0) == 0]
    print(f"\n  Per-line picks (of {total} contexts):")
    for lid in line_ids:
        n = line_picks.get(lid, 0)
        marker = "  DEAD" if n == 0 else ""
        print(f"    {lid:42} {n:6}{marker}")

    if dead:
        print(f"\n  ✗ {len(dead)} dead line(s) — never picked in any swept "
              f"context (shadowed by a later always-true patch on the same "
              f"key, or unreachable):")
        for lid in dead:
            print(f"    - {lid}")
    else:
        print("\n  ✓ every authored line is reachable in the sweep")
    return len(dead)


def main() -> int:
    p = argparse.ArgumentParser(description="Authored-line coverage report")
    p.add_argument("--npc", help="Only report this NPC (matches YAML `npc:`)")
    p.add_argument("--fail-on-dead", action="store_true",
                   help="Exit 1 if any authored line is dead")
    args = p.parse_args()

    overrides_by_npc = load_overrides()
    if not overrides_by_npc:
        print("✗ No built CP fragments — run: python3 tools/build_cp.py",
              file=sys.stderr)
        return 1

    total_dead = 0
    reported = 0
    for yaml_path in sorted(SOURCE.glob("*.yaml")):
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if args.npc and data.get("npc") != args.npc:
            continue
        total_dead += report_npc(yaml_path, overrides_by_npc)
        reported += 1

    if reported == 0:
        print(f"✗ No dialogue YAML matched --npc {args.npc!r}", file=sys.stderr)
        return 1

    print(f"\nTotal dead lines: {total_dead}")
    return 1 if (args.fail_on_dead and total_dead) else 0


if __name__ == "__main__":
    sys.exit(main())
