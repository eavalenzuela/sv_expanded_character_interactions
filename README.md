# Expanded Character Interactions (ECI)

A Stardew Valley mod that makes NPCs feel alive — richer dialogue variance,
branching choices that matter, and a world where things happen between
characters whether or not the player is watching.

**Status:** pre-alpha. Currently scoping the MVP (see `docs/` once written).

## Pillars
1. **Dialogue variance & depth** — context-aware lines (weather, season,
   location, time, day, recent player actions) instead of the same 3 vanilla
   lines on repeat.
2. **Branching choices with consequences** — multi-axis affinity (trust,
   respect, romantic interest) shifted by dialogue answers and remembered
   across the save.
3. **Living world** — NPC-to-NPC relationships simulated off-screen; gossip
   propagates; schedules adapt.

## MVP scope
Four NPCs — **Shane, Leah, Abigail, Sebastian** — with ~40 new context-aware
lines each. No affinity, mood, or simulation yet — just proving the pipeline
end-to-end.

## Repo layout
```
source/         human-authored YAML dialogue + tone guides
tools/          Python scripts (harvest, voice analysis, CP build)
harvest/        gitignored: vanilla dialogue extracted from local install
build/          gitignored: generated Content Patcher JSON
ECI.Tokens/     C# SMAPI mod — registers Content Patcher tokens
ECI.Content/    Content Patcher pack — generated content.json + fragments
```

## Requirements
- Stardew Valley with SMAPI ≥ 4.0 and Content Patcher ≥ 2.0
- Python 3.10+ for authoring tools
- .NET 6 SDK for building `ECI.Tokens`

## License
TBD.
