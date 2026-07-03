# Planned improvements & features

Working plan for this maintenance pass. Improvements target existing
behavior/robustness/docs; features add new capability. Each item lists a
one-line rationale.

## Improvements

1. **Fix the stale simulator scenario in `tools/test_scenarios.yaml`** — the
   "Leah at home on a Mon → vanilla" scenario predates `leah_dow_mon_start` /
   `leah_loc_town_pretty` and has been failing (7/8) ever since; update it to
   the current expected winner.
2. **Extend `tools/test_scenarios.yaml` to Shane, Abigail, and Sebastian** —
   only Linus and Leah have selection-simulator coverage today, so regressions
   in the other three authored NPCs go undetected.
3. **Lint ECI custom-token *values*** — a typo like `chopedTree` or `Morning`
   in a `when:` block currently builds fine and silently never fires in-game;
   validate `PlayerDidToday` flags and `TimeOfDayBucket` buckets against the
   known sets.
4. **Lint branching questions: fallback keys, duplicate ids, vanilla `$q`
   collisions** — the modding guide calls these out as "authoring-time
   validation that pays off": fallback must be `"null"` or an existing key,
   `question.id` must be unique across files, and colliding with a vanilla
   `$q` id (harvested from baseline dialogue) corrupts answer tracking.
5. **Lint responses: duplicate response ids + missing followups** — duplicate
   response ids currently surface as a raw `ValueError` mid-build, and a
   missing `followup` ships a literal `"..."` placeholder to players; both
   deserve lint-time reporting.
6. **Model affinity Query conditions in `simulate_selection.py` and add
   `expect:` coverage** — `--check-yaml` currently checks 0 lines, and
   affinity-gated lines are "unmodelable"; teach the simulator the
   `Query: {{…/Affinity<NPC><Axis>}} op N` form build_cp emits, add an
   `affinity` context knob, validate `expect:` blocks in lint, and add
   expect blocks to reachable lines in all five dialogue YAMLs.
7. **Harden the `eci_affinity` console command** — `eci_affinity set leah
   trust 5` today writes a lowercase `leah/trust` bucket that the
   `AffinityLeahTrust` CP token never reads (silent no-op); canonicalize
   NPC/axis casing, warn on unknown names, and add `add`/`reset` subcommands.
8. **Clamp affinity values in `Affinity`** — deltas re-apply every time a
   player re-answers a repeating question, so values can drift unboundedly;
   clamp to a documented ±100 range.
9. **Test-harness assertion + input hardening** — add a `TextNotContains`
   assertion (turning `linus_smoke.yaml`'s intentional always-FAIL scenario
   into a real passing negative test) and validate `eci_settime` (HHMM range)
   and `eci_setfriendship` (0–14 hearts) arguments.
10. **Docs/meta refresh** — README still says "pre-alpha, scoping the MVP"
    and omits the test harness, scenarios dir, and tool commands; also prune
    unused `pyproject.toml` deps (jinja2/jsonschema/scikit-learn — nothing
    imports them) and document the "always-true axis shadows every earlier
    patch on the same key" CP load-order pitfall in the modding guide.

## New features

1. **Mod-provided API on ECI.Tokens** — expose
   `GetAffinity`/`SetAffinity`/`AdjustAffinity`/`GetPlayerDidTodayFlags` via
   SMAPI's `GetApi`, and consume it from the test harness: scenario files gain
   a `setup.affinity` block (the branching-gated scenario becomes
   self-contained instead of "run `eci_affinity set` first"), and `eci_state`
   prints live affinity.
2. **`tools/coverage_report.py`** — sweep realistic context combinations
   (season × weekday × weather × time bucket × location × recent-action ×
   hearts) through the selection simulator and report per-line pick rates and
   dead (never-picked) lines; the always-true time/DOW axes provably shadow
   the season and weather axes today, and this makes that visible per NPC.
3. **Translation-ready builds (i18n extraction)** — `build_cp.py` now emits
   `{{i18n:…}}` references and generates `ECI.Content/i18n/default.json` from
   authored text (Content Patcher best practice), with question/response/
   followup texts as separate translation units; the simulator resolves i18n
   refs so scenario text assertions keep working.
4. **Pillar-2 second NPC: Shane branching question** — a Charlie-the-chicken
   question (id 1602) at Marnie's in the morning with three affinity-weighted
   responses plus a Trust-gated follow-up line, proving the multi-NPC
   responses.json path; includes simulator scenarios and in-game scenario
   files using the new `setup.affinity`.
5. **New `PlayerDidToday` flags: `visitedBeach`/`visitedTown`/`visitedSaloon`**
   — cheap warp-tracked flags in ECI.Tokens plus new authored recent-action
   lines for Leah and Shane that use them, widening the "the world noticed
   what you did" axis beyond stats-based flags.
