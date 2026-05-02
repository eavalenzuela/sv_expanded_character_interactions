#!/usr/bin/env python3
"""Analyze harvested vanilla dialogue and emit draft tone guides.

Generates a guide for *every* NPC found in harvest/baseline_dialogue/
(38+ characters), so future-phase NPCs already have voice data ready.

The four focal MVP NPCs (Shane, Leah, Abigail, Sebastian) are flagged in
their guide and additionally pull in their event-script lines.

Reads:
  harvest/baseline_dialogue/<NPC>.json     (every NPC's main dialogue)
  harvest/baseline_marriage/MarriageDialogue<NPC>.json (marriageable NPCs)
  harvest/events/*.json                    (event lines for focal NPCs)

Writes:
  source/tone_guides/<npc>.md              (only if file does not exist)
  source/tone_guides/<npc>.md.regen        (if file exists; preserves edits)
"""
from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HARVEST = REPO / "harvest"
OUT_DIR = REPO / "source" / "tone_guides"

FOCAL = {"Shane", "Leah", "Abigail", "Sebastian"}

# ---------- token stripping ----------

CHANCE_RE = re.compile(r"\$c\s+\d+(?:\.\d+)?")
TOKEN_RE = re.compile(r"\$[a-zA-Z0-9]+")
PERCENT_RE = re.compile(r"%[a-zA-Z]+\d*")
GENDER_RE = re.compile(r"\^[^\^]+\^[^\^]+")
CURLY_RE = re.compile(r"\{\{[^}]+\}\}")
HASH_RE = re.compile(r"#")
AT_RE = re.compile(r"@")
SPACE_RE = re.compile(r"\s+")


def strip_tokens(s: str) -> str:
    s = CHANCE_RE.sub(" ", s)
    s = TOKEN_RE.sub(" ", s)
    s = PERCENT_RE.sub(" ", s)
    s = GENDER_RE.sub(" ", s)
    s = CURLY_RE.sub(" ", s)
    s = HASH_RE.sub(" ", s)
    s = AT_RE.sub(" ", s)
    return SPACE_RE.sub(" ", s).strip()


# ---------- dialogue ingestion ----------

def categorize(key: str) -> str:
    k = key
    if k.startswith(("AcceptGift", "RejectGift", "AcceptBirthdayGift")):
        return "gift"
    if k.startswith(("FlowerDance", "danceRejection", "Resort")):
        return "festival"
    if k.startswith(("married_", "dating_")):
        return "relationship"
    if k.startswith("eventSeen_") or "_memory_" in k:
        return "callback"
    if k.startswith(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")):
        return "weekday"
    if any(s in k for s in ("_spring", "_summer", "_fall", "_winter")):
        return "season"
    if any(w in k for w in ("_rain", "_snow", "_storm", "_sunny")):
        return "weather"
    if k.startswith("Introduction"):
        return "intro"
    return "general"


def load_main_dialogue(npc: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    path = HARVEST / "baseline_dialogue" / f"{npc}.json"
    if not path.exists():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    for k, v in data.items():
        if isinstance(v, str) and v.strip():
            out.append((k, v, categorize(k)))
    return out


def load_marriage_dialogue(npc: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    path = HARVEST / "baseline_marriage" / f"MarriageDialogue{npc}.json"
    if not path.exists():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    for k, v in data.items():
        if isinstance(v, str) and v.strip():
            out.append((k, v, "marriage"))
    return out


EVENT_SPEAK_RE = re.compile(r'(?:^|/)(?:speak|end\s+dialogue)\s+(\w+)\s+"((?:[^"\\]|\\.)*)"')


def load_event_dialogue(npc: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    events_dir = HARVEST / "events"
    if not events_dir.exists():
        return out
    for path in sorted(events_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for event_key, script in data.items():
            if not isinstance(script, str):
                continue
            for m in EVENT_SPEAK_RE.finditer(script):
                if m.group(1) != npc:
                    continue
                eid = event_key.split("/")[0]
                key = f"event:{path.stem}:{eid}"
                line = m.group(2).replace('\\"', '"')
                out.append((key, line, "event"))
    return out


def load_all(npc: str) -> list[tuple[str, str, str]]:
    return load_main_dialogue(npc) + load_marriage_dialogue(npc) + load_event_dialogue(npc)


def discover_npcs() -> list[str]:
    base = HARVEST / "baseline_dialogue"
    return sorted(p.stem for p in base.glob("*.json")) if base.exists() else []


# ---------- stats ----------

WORD_RE = re.compile(r"[A-Za-z']+")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
CONTRACTION_RE = re.compile(r"\b\w+'(?:s|t|re|ve|d|ll|m)\b", re.IGNORECASE)


def words(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def fingerprint(clean_lines: list[str]) -> dict:
    blob = " ".join(clean_lines)
    word_list = words(blob)
    n_words = max(1, len(word_list))
    sentences = [s for s in SENT_SPLIT_RE.split(blob) if s.strip()]
    sent_lens = [len(words(s)) for s in sentences if words(s)]

    def per100(count: int) -> float:
        return round(100 * count / n_words, 2)

    ellipsis = blob.count("...") + blob.count("…")
    emdash = blob.count("—") + blob.count("--")

    return {
        "lines": len(clean_lines),
        "words": n_words,
        "sentence_len_mean": round(statistics.mean(sent_lens), 1) if sent_lens else 0,
        "sentence_len_median": int(statistics.median(sent_lens)) if sent_lens else 0,
        "exclam": per100(blob.count("!")),
        "question": per100(blob.count("?")),
        "ellipsis": per100(ellipsis),
        "emdash": per100(emdash),
        "comma": per100(blob.count(",")),
        "contraction": per100(len(CONTRACTION_RE.findall(blob))),
        "ttr": round(len(set(word_list)) / n_words, 3),
    }


# ---------- tf-idf ----------

STOPWORDS = set(
    """
    a about above after again against all am an and any are aren as at be because been before being
    below between both but by can could did do does doing don down during each few for from further
    had has have having he her here hers herself him himself his how i if in into is isn it its itself
    just like ll m me might more most must my myself no nor not now of off on once only or other our
    ours ourselves out over own re s same shan she should so some such t than that the their theirs
    them themselves then there these they this those through to too under until up ve very was wasn
    we were what when where which while who whom why will with won would y you your yours yourself
    yourselves
    yeah ok okay hey oh well hmm uh huh um get got go going know think want need feel really pretty
    kind thing things stuff something someone everyone never always maybe gonna let lets it d ll
    """.split()
)


def vocab_filter(ws: list[str]) -> Counter[str]:
    return Counter(w for w in ws if w not in STOPWORDS and len(w) > 2 and w.isalpha())


def tfidf_all(per_npc_words: dict[str, list[str]], top_n: int = 25) -> dict[str, list[tuple[str, float]]]:
    """tf-idf across the full NPC set — every NPC contributes to df and gets scored."""
    tf: dict[str, Counter[str]] = {npc: vocab_filter(ws) for npc, ws in per_npc_words.items()}
    df: Counter[str] = Counter()
    for c in tf.values():
        for term in c:
            df[term] += 1
    n_docs = len(per_npc_words)

    out: dict[str, list[tuple[str, float]]] = {}
    for npc, c in tf.items():
        total = max(1, sum(c.values()))
        scored = []
        for term, freq in c.items():
            if freq < 3:
                continue
            idf = math.log((n_docs + 1) / (1 + df[term])) + 1
            scored.append((term, (freq / total) * idf))
        scored.sort(key=lambda x: -x[1])
        out[npc] = scored[:top_n]
    return out


# ---------- sample picking ----------

def pick_samples(items: list[tuple[str, str]], n: int = 6) -> list[tuple[str, str]]:
    if len(items) <= n:
        return items
    sorted_items = sorted(items, key=lambda x: len(x[1]))
    mid = len(sorted_items) // 2
    return sorted_items[:2] + sorted_items[mid : mid + 2] + sorted_items[-2:]


# ---------- output ----------

def render_guide(npc: str, fp: dict, distinctive: list[tuple[str, float]],
                 cats: dict[str, list[tuple[str, str]]], total_entries: int,
                 is_focal: bool) -> str:
    L: list[str] = []
    L.append(f"# {npc} — Voice Guide")
    L.append("")
    if is_focal:
        L.append("> **Focal NPC for MVP** — full pass needed before authoring new lines.")
    else:
        L.append("> **Future-phase NPC** — captured for reference; prioritize the four focal NPCs first.")
    L.append("")
    L.append(
        "> **Auto-generation:** quantitative sections regenerate via "
        "`tools/analyze_voice.py`. Qualitative sections (Snapshot, Register, "
        "Topics, Negative space, Verbal tics, Mood) need a human pass. "
        "Re-running will not overwrite an existing file — it writes a "
        "sibling `.regen` instead."
    )
    L.append("")

    L.append("## Snapshot")
    L.append("_one-line character read — fill in_")
    L.append("")

    L.append("## Voice fingerprint  *(auto)*")
    L.append("")
    L.append(f"- Lines analyzed: **{fp['lines']}** of {total_entries} entries")
    L.append(f"- Words total: **{fp['words']}**")
    L.append(f"- Sentence length: mean **{fp['sentence_len_mean']}** / median **{fp['sentence_len_median']}**")
    L.append(f"- Type-token ratio: **{fp['ttr']}**")
    L.append("")
    L.append("**Per 100 words**")
    L.append("")
    L.append("| `!` | `?` | `...` | `—`/`--` | `,` | contractions |")
    L.append("|-----|-----|-------|----------|-----|--------------|")
    L.append(
        f"| {fp['exclam']} | {fp['question']} | {fp['ellipsis']} | "
        f"{fp['emdash']} | {fp['comma']} | {fp['contraction']} |"
    )
    L.append("")

    L.append("## Distinctive vocabulary  *(auto, vs. all vanilla NPCs)*")
    L.append("")
    L.append(", ".join(f"`{w}`" for w, _ in distinctive[:20]) if distinctive else "_(insufficient data)_")
    L.append("")

    L.append("## Register")
    L.append("- Default: ")
    L.append("- With trusted player: ")
    L.append("- Under stress / when annoyed: ")
    L.append("")
    L.append("## Topics they pursue")
    L.append("- ")
    L.append("")
    L.append("## Topics they avoid / deflect")
    L.append("- ")
    L.append("")
    L.append("## Lines they would never say  *(negative space)*")
    L.append("- ")
    L.append("")
    L.append("## Verbal tics / pet phrases")
    L.append("- ")
    L.append("")
    L.append("## Mood shifts (preview for Phase 3)")
    L.append("- Happy: ")
    L.append("- Tired/down: ")
    L.append("- Annoyed: ")
    L.append("")

    L.append("## Sample lines by category  *(auto)*")
    L.append("")
    cat_order = [
        "intro", "general", "weekday", "season", "weather",
        "festival", "gift", "relationship", "marriage", "callback", "event",
    ]
    seen: set[str] = set()
    for cat in cat_order + sorted(cats.keys()):
        if cat in seen or cat not in cats:
            continue
        seen.add(cat)
        items = cats[cat]
        samples = pick_samples(items, n=6)
        L.append(f"### {cat} — {len(items)} total, {len(samples)} sampled")
        L.append("")
        for key, raw in samples:
            text = raw.replace("\n", " ").replace("|", "\\|")
            L.append(f"- **`{key}`** — {text}")
        L.append("")

    return "\n".join(L).rstrip() + "\n"


# ---------- main ----------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    npcs = discover_npcs()
    if not npcs:
        print("✗ No baseline_dialogue/ found. Run setup_harvest.sh first.")
        return

    print(f"→ Discovered {len(npcs)} NPCs in baseline corpus")

    all_dialogue = {npc: load_all(npc) for npc in npcs}

    per_npc_words = {
        npc: words(" ".join(strip_tokens(raw) for _, raw, _ in entries))
        for npc, entries in all_dialogue.items()
    }
    distinctive = tfidf_all(per_npc_words)

    print(f"→ Generating tone guides → {OUT_DIR}")

    n_new = n_regen = 0
    for npc in npcs:
        entries = all_dialogue[npc]
        clean_lines = [c for c in (strip_tokens(raw) for _, raw, _ in entries) if c]
        if not clean_lines:
            continue
        fp = fingerprint(clean_lines)

        cats: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for key, raw, cat in entries:
            cleaned = strip_tokens(raw)
            if cleaned:
                cats[cat].append((key, cleaned))

        guide = render_guide(npc, fp, distinctive[npc], cats, len(entries), is_focal=npc in FOCAL)
        target = OUT_DIR / f"{npc.lower()}.md"
        if target.exists():
            (OUT_DIR / f"{npc.lower()}.md.regen").write_text(guide, encoding="utf-8")
            n_regen += 1
        else:
            target.write_text(guide, encoding="utf-8")
            n_new += 1

    print(f"  · {n_new} new guide(s), {n_regen} .regen file(s)")
    if FOCAL:
        focal_seen = sorted(FOCAL & set(npcs))
        print(f"  · focal NPCs covered: {', '.join(focal_seen)}")
        missing = sorted(FOCAL - set(npcs))
        if missing:
            print(f"  ! focal NPCs missing from corpus: {', '.join(missing)}")


if __name__ == "__main__":
    main()
