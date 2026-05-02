#!/usr/bin/env bash
# Downloads StardewXnbHack, runs it against the local Stardew Valley install,
# and copies the dialogue/strings/events/schedules we care about into ./harvest/.
#
# Idempotent: re-running re-uses the cached download and re-extracts only what's
# needed. Safe: any files staged into the game directory are tracked and removed
# on exit (including Ctrl-C).
#
# Override the install path with: ECI_GAME_DIR=/path/to/Stardew\ Valley ./setup_harvest.sh

set -euo pipefail

GAME_DIR="${ECI_GAME_DIR:-/games/games/steam/steamapps/common/Stardew Valley}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$REPO_ROOT/tools/_vendor"
HARVEST_DIR="$REPO_ROOT/harvest"
XNBHACK_DIR="$VENDOR_DIR/StardewXnbHack"
UNPACKED_DIR="$GAME_DIR/Content (unpacked)"

NPCS=("Shane" "Leah" "Abigail" "Sebastian")

if [[ ! -d "$GAME_DIR" ]]; then
  echo "✗ Game directory not found: $GAME_DIR" >&2
  echo "  Set ECI_GAME_DIR=/your/path and re-run." >&2
  exit 1
fi
if [[ ! -f "$GAME_DIR/Stardew Valley.dll" ]]; then
  echo "✗ Stardew Valley.dll not found in $GAME_DIR" >&2
  exit 1
fi
command -v gh >/dev/null    || { echo "✗ gh CLI not in PATH" >&2; exit 1; }
command -v unzip >/dev/null || { echo "✗ unzip not in PATH" >&2; exit 1; }

mkdir -p "$VENDOR_DIR" "$HARVEST_DIR/dialogue" "$HARVEST_DIR/events" \
         "$HARVEST_DIR/strings" "$HARVEST_DIR/schedules" \
         "$HARVEST_DIR/baseline_dialogue"

# 1) Fetch StardewXnbHack Linux release if not cached.
XNBHACK_BIN="$XNBHACK_DIR/StardewXnbHack"
if [[ ! -x "$XNBHACK_BIN" ]]; then
  echo "→ Downloading latest StardewXnbHack (Linux) release…"
  rm -rf "$XNBHACK_DIR"
  mkdir -p "$XNBHACK_DIR"
  (
    cd "$XNBHACK_DIR"
    gh release download --repo Pathoschild/StardewXnbHack --pattern "*Linux*.zip"
    zip_file="$(ls *Linux*.zip | head -1)"
    unzip -q "$zip_file"
    rm -f "$zip_file"
    # Release zips wrap the binary in a "StardewXnbHack X.Y.Z for Linux" folder.
    found="$(find . -maxdepth 3 -type f -name StardewXnbHack | head -1)"
    if [[ -n "$found" && "$found" != "./StardewXnbHack" ]]; then
      mv "$found" ./StardewXnbHack
      # Clean up empty wrapper directory.
      find . -mindepth 1 -type d -empty -delete
    fi
    chmod +x StardewXnbHack
  )
fi

if [[ ! -x "$XNBHACK_BIN" ]]; then
  echo "✗ StardewXnbHack binary not found after extraction in $XNBHACK_DIR" >&2
  exit 1
fi

# 2) Symlink the binary into the game directory — the tool resolves its own
#    location and refuses to run unless it's inside the game folder. Tracked
#    for cleanup so we don't pollute the install.
STAGED=()
cleanup() {
  for p in "${STAGED[@]+"${STAGED[@]}"}"; do
    rm -rf "$p"
  done
}
trap cleanup EXIT INT TERM

LINKED_BIN="$GAME_DIR/StardewXnbHack"
if [[ ! -e "$LINKED_BIN" ]]; then
  # Hard copy, not symlink — the tool resolves symlinks and would land back in
  # the vendor dir and refuse to run.
  cp "$XNBHACK_BIN" "$LINKED_BIN"
  chmod +x "$LINKED_BIN"
  STAGED+=("$LINKED_BIN")
fi

SETTINGS_PATH="$GAME_DIR/StardewXnbHack.settings.json"
if [[ ! -e "$SETTINGS_PATH" ]]; then
  cat > "$SETTINGS_PATH" <<'JSON'
{
  "ShowPressAnyKeyToExit": false
}
JSON
  STAGED+=("$SETTINGS_PATH")
fi

# 3) Run from the game directory.
#    The tool always tries to read a key on exit and blows up under redirected
#    stdin. We suppress that traceback (the actual unpack already succeeded by
#    that point) and the non-zero exit code.
echo "→ Running StardewXnbHack (unpacking ~all XNB content; takes a minute)…"
# The tool's "press any key" prompt always crashes under redirected stdin and
# dumps a stack trace AFTER the unpack has already finished. Capture all
# output, surface only the success line, and detect real failure by checking
# that Content (unpacked)/ was produced.
LOG_FILE="$(mktemp)"
(
  cd "$GAME_DIR"
  # `set +m` disables job control so bash doesn't print "Aborted (core dumped)".
  set +m
  ./StardewXnbHack < /dev/null
) >"$LOG_FILE" 2>&1 || true
if grep -q '^Done! Unpacked' "$LOG_FILE"; then
  grep '^Done! Unpacked' "$LOG_FILE"
else
  echo "✗ StardewXnbHack failed. Full log:" >&2
  cat "$LOG_FILE" >&2
  rm -f "$LOG_FILE"
  exit 1
fi
rm -f "$LOG_FILE"

if [[ ! -d "$UNPACKED_DIR" ]]; then
  echo "✗ Expected unpacked output at: $UNPACKED_DIR" >&2
  exit 1
fi

# 4) Copy the subset we care about into harvest/.
echo "→ Harvesting dialogue / strings / events / schedules…"

copy_if_exists() {
  local src="$1" dst="$2"
  if [[ -e "$src" ]]; then
    cp -r "$src" "$dst"
  fi
}

for npc in "${NPCS[@]}"; do
  copy_if_exists "$UNPACKED_DIR/Characters/Dialogue/${npc}.json"        "$HARVEST_DIR/dialogue/"
  copy_if_exists "$UNPACKED_DIR/Characters/Dialogue/${npc}_Beach.json"  "$HARVEST_DIR/dialogue/"
  copy_if_exists "$UNPACKED_DIR/Characters/Dialogue/${npc}_Winter.json" "$HARVEST_DIR/dialogue/"
  copy_if_exists "$UNPACKED_DIR/Characters/Dialogue/MarriageDialogue${npc}.json" "$HARVEST_DIR/dialogue/"
  copy_if_exists "$UNPACKED_DIR/Characters/schedules/${npc}.json"       "$HARVEST_DIR/schedules/"
done

# Baseline corpus: every NPC's main dialogue file (English only, exclude
# marriage/seasonal variants). Used by analyze_voice.py to score tf-idf and
# generate tone guides for every NPC for future-phase expansion.
if [[ -d "$UNPACKED_DIR/Characters/Dialogue" ]]; then
  find "$UNPACKED_DIR/Characters/Dialogue" -maxdepth 1 -name '*.json' \
       ! -regex '.*\.[a-z][a-z]-[A-Z][A-Z]\.json' \
       ! -name 'MarriageDialogue*.json' \
       ! -name '*_Beach.json' ! -name '*_Winter.json' \
       ! -name 'Baby*.json' ! -name 'Assorted_*.json' \
       -exec cp {} "$HARVEST_DIR/baseline_dialogue/" \;
fi

# Marriage dialogue for every marriageable NPC.
mkdir -p "$HARVEST_DIR/baseline_marriage"
if [[ -d "$UNPACKED_DIR/Characters/Dialogue" ]]; then
  find "$UNPACKED_DIR/Characters/Dialogue" -maxdepth 1 -name 'MarriageDialogue*.json' \
       ! -regex '.*\.[a-z][a-z]-[A-Z][A-Z]\.json' \
       -exec cp {} "$HARVEST_DIR/baseline_marriage/" \;
fi

# Strings — small enough to take wholesale; harvest_vanilla.py will filter.
copy_if_exists "$UNPACKED_DIR/Strings/Characters.json"      "$HARVEST_DIR/strings/"
copy_if_exists "$UNPACKED_DIR/Strings/SpeechBubbles.json"   "$HARVEST_DIR/strings/"
copy_if_exists "$UNPACKED_DIR/Strings/StringsFromCSFiles.json" "$HARVEST_DIR/strings/"

# Events — keep English-only per-location files (skip *.xx-XX.json variants).
# The analyzer filters by NPC name within these files.
if [[ -d "$UNPACKED_DIR/Data/Events" ]]; then
  find "$UNPACKED_DIR/Data/Events" -maxdepth 1 -name '*.json' \
       ! -regex '.*\.[a-z][a-z]-[A-Z][A-Z]\.json' \
       -exec cp {} "$HARVEST_DIR/events/" \;
fi

# Gift tastes & NPC dispositions for context.
copy_if_exists "$UNPACKED_DIR/Data/NPCGiftTastes.json"    "$HARVEST_DIR/"
copy_if_exists "$UNPACKED_DIR/Data/NPCDispositions.json"  "$HARVEST_DIR/"
copy_if_exists "$UNPACKED_DIR/Data/Characters.json"       "$HARVEST_DIR/"

echo "✓ Harvest complete → $HARVEST_DIR"
echo "  Dialogue files: $(ls -1 "$HARVEST_DIR/dialogue" 2>/dev/null | wc -l)"
echo "  Event files:    $(ls -1 "$HARVEST_DIR/events" 2>/dev/null | wc -l)"
echo "  Baseline NPCs:  $(ls -1 "$HARVEST_DIR/baseline_dialogue" 2>/dev/null | wc -l)"
echo "  Marriage files: $(ls -1 "$HARVEST_DIR/baseline_marriage" 2>/dev/null | wc -l)"

# 5) Reclaim disk: the unpacked dump is ~176MB and we've already copied what
#    we need. Pass ECI_KEEP_UNPACKED=1 to skip this for faster re-runs.
if [[ "${ECI_KEEP_UNPACKED:-0}" != "1" && -d "$UNPACKED_DIR" ]]; then
  echo "→ Removing $UNPACKED_DIR (set ECI_KEEP_UNPACKED=1 to keep)"
  rm -rf "$UNPACKED_DIR"
fi
