# Expanded Character Interactions (ECI)

A Stardew Valley mod that makes NPCs feel alive — richer dialogue variance,
branching choices that matter, and a world where things happen between
characters whether or not the player is watching.

**Status:** pre-alpha.
- **Pillar 1 MVP complete** — Shane, Leah, Abigail, and Sebastian each have
  ~44 context-aware lines across six axes (season, weather, time-of-day,
  day-of-week, location, recent player action), validated in-game.
- **Pillar 2 onramp landed** — multi-axis affinity (Trust/Respect/Romance)
  persisted per save, shifted by branching `$q`/`$r` dialogue answers, and
  fed back into Content Patcher via `Affinity<NPC><Axis>` tokens. Leah and
  Shane each have a branching question with a trust-gated follow-up.
- Pillar 3 not started.

## Pillars
1. **Dialogue variance & depth** — context-aware lines (weather, season,
   location, time, day, recent player actions) instead of the same 3 vanilla
   lines on repeat.
2. **Branching choices with consequences** — multi-axis affinity (trust,
   respect, romantic interest) shifted by dialogue answers and remembered
   across the save.
3. **Living world** — NPC-to-NPC relationships simulated off-screen; gossip
   propagates; schedules adapt.

## Repo layout
```
source/dialogue/     human-authored YAML dialogue (one file per NPC)
source/scenarios/    YAML scenarios for the in-game test harness
source/tone_guides/  per-NPC voice guides (generated + hand-edited)
tools/               Python authoring pipeline (see below)
harvest/             gitignored: vanilla dialogue extracted from local install
ECI.Tokens/          C# SMAPI mod — CP tokens, affinity store, mod API
ECI.Content/         Content Patcher pack — generated fragments + i18n
ECI.TestHarness/     C# SMAPI mod — diagnostic console commands + scenario runner
```

## Authoring pipeline
```
python3 tools/lint_dialogue.py        # static checks on source/dialogue/*.yaml
python3 tools/build_cp.py             # lint + emit CP fragments, i18n/default.json,
                                      #   and ECI.Tokens/responses.json
python3 tools/build_scenarios.py      # source/scenarios/*.yaml → harness JSON
python3 tools/simulate_selection.py --scenarios tools/test_scenarios.yaml
                                      # predict which key/text Stardew picks
python3 tools/simulate_selection.py --check-yaml
                                      # verify authored lines reach their
                                      #   intended context (expect: blocks)
python3 tools/coverage_report.py      # sweep contexts; find dead/shadowed lines
```
`tools/setup_harvest.sh` extracts vanilla dialogue from a local install into
`harvest/` (required for baseline-aware lint checks and the simulator).

Builds are translation-ready: authored strings land in
`ECI.Content/i18n/default.json` and the generated entries reference them via
`{{i18n:...}}` tokens.

In-game diagnostics (SMAPI console, via ECI.TestHarness + ECI.Tokens):
`eci_dump <NPC>`, `eci_npcdialogue <NPC>`, `eci_state`, `eci_settime`,
`eci_setfriendship`, `eci_affinity show|set|add|reset`, and
`eci_runfile scenarios/<file>.json`.

See `StardewValley_Modding_Guide.md` for the hard-won SMAPI/CP/dialogue
gotchas this repo is built around.

## Requirements
- Stardew Valley 1.6+ with SMAPI ≥ 4.0 and Content Patcher ≥ 2.0
- Python 3.10+ (PyYAML) for authoring tools
- .NET 6 SDK for building `ECI.Tokens` and `ECI.TestHarness`

## License
TBD.
