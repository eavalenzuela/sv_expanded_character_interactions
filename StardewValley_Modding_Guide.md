# Stardew Valley Modding Guide

Hard-won knowledge from building this mod. Read before touching SMAPI, Content Patcher (CP), or Stardew internals — most of these aren't documented anywhere obvious, and many surface as silent rejections or runtime crashes only when a player exercises a specific code path.

Toolchain: SMAPI ≥ 4.0, Content Patcher ≥ 2.0, Stardew Valley 1.6+, .NET 6, Pathoschild's `ModBuildConfig` package.

---

## Launch & process

- **Always launch via the `StardewValley` shell wrapper**, not `StardewModdingAPI` directly. The binary needs `LD_LIBRARY_PATH=.` to resolve `libGalaxyCSharpGlue`; the wrapper sets it. Direct launch fails with `DllNotFoundException`.
- The `libGalaxyCSharpGlue` / `Galaxy.Api` `TypeInitializationException` lines on Linux Steam are **non-fatal and expected** — GOG Galaxy interop. Skip past them. Look for `Registered CP tokens: …` to confirm your mod actually loaded.
- The wrapper opens a separate terminal window for the SMAPI console by default. Pass `--use-current-shell` (or `SMAPI_USE_CURRENT_SHELL=true`) to keep logs in the current shell — but then you have **no interactive prompt**, so console commands like `eci_runfile`, `patch reload`, etc. can't be typed.
- SMAPI's persistent log lives at `~/.config/StardewValley/ErrorLogs/SMAPI-latest.txt` — tail this for diagnostics across launches.

## Hot-reload limits

- `patch reload <UniqueID>` re-runs CP for one pack. Picks up YAML/JSON content edits.
- It does **NOT** refresh an open `DialogueBox` — if a dialogue is broken (e.g., missing fallback, missing followup), reload doesn't free you. ESC out or quit and relaunch.
- It does **NOT** reload C# DLLs. Any change to a SMAPI mod's compiled output (`ECI.Tokens.dll`, Harmony patches, etc.) requires a full game relaunch.
- ECI.Content is symlinked into the Mods folder for free hot-iteration. The C# mods are deployed via `ModBuildConfig`'s `<EnableModDeploy>true</EnableModDeploy>` on every `dotnet build`.

---

## Content Patcher tokens

### Token names must be alphabetical-only
CP **silently rejects** token names with underscores, digits, or hyphens, with a single ERROR-level log line per rejection. Your `RegisterToken(...)` call appears to succeed (no exception), but the token never enters the namespace, and any patch referencing it fails with `// invalid tokens: …` in `patch summary`.

```csharp
// WRONG — silently rejected, no compile error
cp.RegisterToken(manifest, "Affinity_Leah_Trust", getValue);

// RIGHT — alphabetical-only
cp.RegisterToken(manifest, "AffinityLeahTrust", getValue);
```

### Tokens are re-evaluated on CP "context updates", not on every state change
By default a patch's `Update` field triggers re-evaluation. Common values: `OnDayStart` (default), `OnLocationChange`, `OnTimeChange`. Combinations: `"OnLocationChange,OnTimeChange"`.

A mid-day change to a custom token's underlying state (e.g., the player picks a dialogue response that bumps an affinity int) does not, by itself, trigger CP to re-apply patches. The player must perform an action that fires one of the listed `Update` events. Walking out and back into a location is the simplest forcing function.

If a patch's `When` references a custom token and you want the patch to re-apply on token change without a location/time event, you'd need `OnTimeChange` plus a fast-changing token, or extend CP integration. (We haven't validated `OnTokenChange` semantics for custom tokens here yet.)

### Query syntax for arithmetic in `When`
CP doesn't support `>=` etc. as token comparisons directly. The canonical form is a `Query` *key*, not a Query *token*:

```json
"When": {
  "LocationName": "LeahHouse",
  "Query: {{your.Mod/SomeTokenName}} >= 5": "true"
}
```

- The whole key is the literal string `"Query: <expr>"`. **Not** wrapped in `{{…}}`.
- Inner token references **do** use `{{…}}`.
- Operators: `>=`, `<=`, `>`, `<`, `=`, `<>`. **Not** `==` and **not** `!=`. Translate from author syntax at build time.
- The value is the string `"true"` (the expected Query result).

### CP load-order resolution
When multiple `EditData` patches target the same key in the same dictionary and all `When` clauses match, the **later patch in the file wins**. This is "last write wins" against the CP-built fragment, in textual order. Author your overrides accordingly: more-specific gates go after less-specific ones in the YAML/JSON.

### Always-true axes shadow everything earlier on the same key
A corollary of last-write-wins that cost us most of two authored axes: if a *set* of later patches jointly covers **every possible context** for a key, every earlier patch on that key is dead — not sometimes-shadowed, *never reachable*.

Concretely: our time-of-day lines cover all four buckets (`morning|midday|evening|late`), and exactly one bucket is always active. Any patch set earlier in the file that targets the same weekday keys (our season and weather axes) can never win — some time-bucket line always matches and overwrites it. Same for day-of-week lines, which are unconditional on their weekday key: they kill everything earlier on that key, and only lose to later location/action/multi-axis lines.

Notes:
- This is invisible in `patch summary` (every patch "applied" — the value just got overwritten) and in lint (each line is individually valid).
- `python3 tools/coverage_report.py` sweeps contexts through the selection simulator and lists dead lines per NPC. As of this writing it reports the season + weather axes (and a couple of others) as fully shadowed for the four focal NPCs — a content-design decision to resolve (rotate axes by day? gate the catch-all axes down?), not a build bug.
- When adding a new axis, decide where it sits in the priority order *first*, then check whether it fully covers the axes below it.

---

## Stardew dialogue syntax

### `$q` — branching question
```
$q <questionId> <fallbackKey>#<questionText>#$r ...
```

- `<questionId>` is an integer. Avoid colliding with vanilla IDs (search the game files if unsure). `1601` worked for us; `50` is Sebastian.
- `<fallbackKey>` is the **dialogue dict key** Stardew falls back to if the player has answered `<questionId>` before. Stardew does `speaker.Dialogue[fallbackKey]` directly — `KeyNotFoundException` if the key doesn't exist.
- The literal string `"null"` is the documented sentinel for "no fallback — skip the lookup". Use this unless you have a real fallback line authored.

```
# Wrong — Leah.Dialogue["fallback"] doesn't exist; crashes second talk
$q 1601 fallback#…

# Right — parser sees "null" and skips the fallback lookup
$q 1601 null#…
```

### `$r` — response (answer)
```
$r <questionId> <friendshipDelta> <responseKey>#<responseText>
```

Two non-obvious behaviors:

1. **Stardew unconditionally calls `speaker.Dialogue[responseKey]` after selection** to fetch a follow-up dialogue line (`Dialogue.chooseResponse` line ~1635). If no entry exists, `KeyNotFoundException` is thrown, the dialogue stack is left in a broken state, and the player gets trapped in the same prompt forever (subsequent clicks throw `Stack empty`).

   **Mitigation:** every `responseKey` must have a matching entry in the NPC's Dialogue dict. Even a `"…"` placeholder is fine. We codify this in `build_cp.py` by emitting a per-response Edit alongside the question.

2. **`Game1.player.dialogueQuestionsAnswered` does NOT track which response was picked.** Stardew calls `farmer.addSeenResponse(playerResponses[i].id)` — and `id` is the **question id**, not the response id. So polling `dialogueQuestionsAnswered` to detect which option was chosen will not work; every option for the same question records the same id.

   **Mitigation:** Harmony-patch `Dialogue.chooseResponse(Response)` with a postfix and read `response.responseKey`. That's the only reliable hook into per-response selection.

### `friendshipDelta` in `$r`
The middle integer in `$r` is applied via `farmer.changeFriendship(delta, speaker)` — i.e., it shifts vanilla friendship hearts. Don't confuse it with custom multi-axis affinity. Keep it `0` if you're applying your own deltas elsewhere (e.g., via Harmony).

---

## Harmony in SMAPI mods

SMAPI bundles Harmony 2.x. Enable it via `csproj`:

```xml
<PropertyGroup>
  <EnableHarmony>true</EnableHarmony>
</PropertyGroup>
```

Then in `ModEntry.Entry`:

```csharp
using HarmonyLib;

internal static ModEntry? Instance;

public override void Entry(IModHelper helper)
{
    Instance = this;
    var harmony = new Harmony(this.ModManifest.UniqueID);
    harmony.Patch(
        original: AccessTools.Method(typeof(StardewValley.Dialogue),
                                     nameof(StardewValley.Dialogue.chooseResponse)),
        postfix: new HarmonyMethod(typeof(ModEntry), nameof(ChooseResponsePostfix)));
}

public static void ChooseResponsePostfix(Response response)
{
    if (response?.responseKey == null) return;
    Instance?.HandleResponse(response.responseKey);
}
```

SMAPI logs `Detected game patcher in assembly <ModName>.dll` on load — confirms Harmony is active. Patches don't hot-reload; quit/relaunch for any change.

---

## NPC dialogue: live asset vs. cached state

Stardew NPCs cache their `Dialogue` dict at certain points (day-start, sometimes on `loadCurrentDialogue`). CP edits the underlying asset, but the NPC instance can hold stale data. Two views to keep separate:

- **Live post-CP asset**: `helper.GameContent.Load<Dictionary<string,string>>("Characters/Dialogue/<NPC>")`. This is what CP has produced and what `eci_dump <NPC>` shows.
- **NPC instance state**: `npc.Dialogue` dict and `npc.CurrentDialogue` stack. This is what the player will actually see when they next interact. `eci_npcdialogue <NPC>` shows this.

If they disagree, you have a cache-staleness bug. CP changes during a session may not propagate to active NPC instances until the next greeting trigger or warp.

---

## Heart events and warping

`Game1.warpFarmer(targetLocation, x, y, false)` is synchronous in initiating the warp but the actual location change happens on the next tick. Two consequences:

- **Immediate post-warp assertions are unreliable.** CP's `LocationName`-based `When` clauses won't have re-evaluated yet, NPC's `currentLocation` may not reflect the warp, and any `OnLocationChange`-gated patch isn't applied.
- **Heart events queued by location preconditions can fire during the warp.** Setting hearts to a low value before warping doesn't always prevent a higher-heart event from triggering if its precondition was already cued. If your test harness warps the player and you see vanilla cutscenes preempting your patches, this is why.

**Bypass:** the SMAPI debug command `debug warp <Location> <x> <y>` teleports past door locks and is reliable for manual testing.

---

## Diagnostic commands worth having

Build these into your test harness early — they pay for themselves in one debugging session:

- `<mod>_dump <NPC>` — print the live CP-patched Dialogue dict (post-CP).
- `<mod>_npcdialogue <NPC>` — print the NPC's in-memory `Dialogue` and `CurrentDialogue.Peek()`.
- `<mod>_state` — print player location, time, weather, friendship, plus any custom token state.
- Setters: `<mod>_settime`, `<mod>_setfriendship`, `<mod>_<custom>`.

The diff between dump (asset) and npcdialogue (cache) is your stale-cache detector. The diff between your own custom-state setter and `patch summary` token output is your token-registration detector.

---

## Authoring-time validation that pays off

- **Lint custom-token-name characters.** Reject any name containing non-alphabetical characters at build time, before CP rejects them silently at runtime.
- **Lint `$q` fallback keys** — either the literal `"null"` or a key that exists in the same NPC's dialogue source.
- **Lint `$r` responseKeys** — every `responseKey` must have a corresponding follow-up dialogue entry. Generate the entries automatically from the question schema; don't trust authors to remember.

---

## Things to verify before relying on them

These are claims I haven't fully validated for this codebase yet — flag if they bite you:

- Whether CP's `OnTokenChange` triggers on custom-mod-provided token changes (not just CP-built-in tokens). We haven't tested it; we work around with explicit location/time triggers.
- Whether `Dialogue.chooseResponse` is the only entry point that consumes `responseKey`. Festival event answers go through `currentEvent.answerDialogueQuestion(speaker, responseKey)` (line 1613) — different code path; Harmony postfix on `chooseResponse` doesn't see those.
- Save data semantics for our `Affinity` class — we're using SMAPI's `helper.Data.WriteSaveData`, which is per-save. Cross-save state would need a different approach.
