#!/usr/bin/env python3
"""Build Content Patcher fragments + branching-dialogue config from YAML.

Reads source/dialogue/*.yaml and emits:
- ECI.Content/include/<npc>.json   (per-NPC CP fragment)
- ECI.Content/content.json         (CP root that Includes the fragments)
- ECI.Tokens/responses.json        (response-id → per-axis affinity deltas)

YAML schema additions for Pillar 2:

  - id: leah_q_about_art
    target_key: any_day
    when:
      LocationName: LeahHouse
      affinity:                  # cleaner than raw {{Query: ...}}
        Leah:
          Trust: ">=0"           # ops: >=, >, <=, <, =, !=
    question:                    # branching dialogue (replaces `text:`)
      id: 1601                   # Stardew question id (unique int)
      fallback: fallback         # fallback dialogue key
      text: "Want to see what I'm working on?"
      responses:
        - id: leah_q_art_yes
          text: "Yes, I'd love to."
          affinity:
            Leah: { Trust: 5, Romance: 2 }
        - id: leah_q_art_maybe
          text: "Maybe another time."
        - id: leah_q_art_no
          text: "Why? It's just rocks."
          affinity:
            Leah: { Trust: -10, Respect: -5 }

Run: python3 tools/build_cp.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from lint_dialogue import lint_all

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "source" / "dialogue"
OUT = REPO / "ECI.Content"
INCLUDE = OUT / "include"
RESPONSES_OUT = REPO / "ECI.Tokens" / "responses.json"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SEASONS = ["spring", "summer", "fall", "winter"]

CP_FORMAT = "2.0.0"
ECI_TOKEN_NAMESPACE = "eavalenzuela.ECI.Tokens"

AFFINITY_OP_RE = re.compile(r"^\s*(>=|<=|!=|==|=|>|<)\s*(-?\d+)\s*$")


def any_day_keys() -> list[str]:
    """28 keys: plain Mon..Sun + <season>_<weekday> for summer/fall/winter."""
    keys = list(WEEKDAYS)
    for s in ("summer", "fall", "winter"):
        keys.extend(f"{s}_{w}" for w in WEEKDAYS)
    return keys


def expand_target_keys(target_key: Any) -> list[str]:
    if isinstance(target_key, str):
        if target_key == "*":
            return WEEKDAYS[:]
        if target_key == "any_day":
            return any_day_keys()
        return [target_key]
    if isinstance(target_key, list):
        out: list[str] = []
        for t in target_key:
            out.extend(expand_target_keys(t))
        return out
    raise ValueError(f"Bad target_key: {target_key!r}")


# ---------- branching dialogue ----------

def build_branching_text(question: dict) -> str:
    """Generate Stardew $q/$r dialogue syntax from a YAML question block.

    Format: $q <qid> <fallback>#<question>#$r <qid> <fp> <rid>#<text>#...

    Stardew's $q parser shows the dialogue at <fallback> if the player has
    already answered <qid>. The literal string "null" is the documented
    "no fallback — skip the lookup" sentinel; any other value must name an
    existing key in the NPC's Dialogue dict or Stardew throws KeyNotFound.
    """
    qid = question["id"]
    fallback = question.get("fallback") or "null"
    qtext = question["text"]
    parts = [f"$q {qid} {fallback}#{qtext}"]
    for r in question.get("responses", []):
        rid = r["id"]
        rtext = r["text"]
        # Vanilla friendship delta is separate from our affinity. Default 0.
        fp = r.get("friendship", 0)
        parts.append(f"$r {qid} {fp} {rid}#{rtext}")
    return "#".join(parts)


def collect_response_deltas(question: dict) -> dict[str, dict[str, dict[str, int]]]:
    """Returns {response_id: {npc: {axis: delta}}} for the responses block."""
    out: dict[str, dict[str, dict[str, int]]] = {}
    for r in question.get("responses", []):
        rid = r["id"]
        affinity = r.get("affinity") or {}
        # Empty {} is intentional (no-op response); preserve so the C# mod
        # registers the response id even if no deltas apply.
        normalized: dict[str, dict[str, int]] = {}
        for npc, axes in affinity.items():
            normalized[npc] = {axis: int(delta) for axis, delta in axes.items()}
        out[rid] = normalized
    return out


# ---------- affinity-gated When clauses ----------

def affinity_to_query_when(when: dict) -> dict:
    """If `when` contains an `affinity:` block, expand each (NPC, axis, expr)
    into a CP `{{Query: ...}}: "true"` entry and return a flat dict suitable
    for CP's When clause. Other When entries are passed through unchanged.

    Supports operators: >= > <= < = == !=
    """
    if "affinity" not in when:
        return dict(when)

    aff = when["affinity"]
    out = {k: v for k, v in when.items() if k != "affinity"}

    for npc, axes in aff.items():
        for axis, expr in axes.items():
            m = AFFINITY_OP_RE.match(str(expr))
            if not m:
                raise ValueError(
                    f"Bad affinity expression for {npc}.{axis}: {expr!r}. "
                    f"Use one of: '>=N', '>N', '<=N', '<N', '=N', '!=N'."
                )
            op, val = m.group(1), m.group(2)
            # Author-friendly operators → CP Query operators.
            # CP Query supports: >= <= > < = <>  (not == or !=).
            if op == "==":
                op = "="
            elif op == "!=":
                op = "<>"
            # CP token names must be alphabetical-only — no underscores. The
            # ECI.Tokens registration uses the same Affinity<NPC><Axis> form.
            token_ref = f"{{{{{ECI_TOKEN_NAMESPACE}/Affinity{npc}{axis}}}}}"
            # CP When-clause Query syntax is a literal key:
            #   "Query: <expression>": "true"
            # NOT wrapped in {{...}}. Inner token refs stay {{...}}.
            out[f"Query: {token_ref} {op} {val}"] = "true"
    return out


# ---------- emit ----------

def build_npc_fragment(
    npc: str,
    lines: list[dict],
    response_registry: dict[str, dict[str, dict[str, int]]],
) -> dict:
    """Build a CP secondary file body for one NPC."""
    changes: list[dict] = []
    for line in lines:
        line_id = line["id"]
        when_raw = line.get("when") or {}
        when = affinity_to_query_when(when_raw)

        # `text:` and `question:` are mutually exclusive. Question wins if
        # present (its expansion fills the dialogue text).
        followup_entries: list[tuple[str, str]] = []  # (response_id, followup_text)

        if "question" in line:
            text = build_branching_text(line["question"])
            for rid, npc_axes in collect_response_deltas(line["question"]).items():
                if rid in response_registry and response_registry[rid] != npc_axes:
                    raise ValueError(
                        f"Duplicate response id {rid!r} with conflicting deltas. "
                        f"Make response IDs globally unique."
                    )
                response_registry[rid] = npc_axes
            # Stardew's Dialogue.chooseResponse does a direct dict access on
            # speaker.Dialogue[responseKey] for the post-selection follow-up.
            # Without an entry, it throws KeyNotFoundException and the player's
            # answer is never recorded in dialogueQuestionsAnswered (so our
            # affinity poll never sees it). Emit one entry per response.
            for r in line["question"].get("responses", []):
                followup_entries.append((r["id"], r.get("followup", "...")))
        else:
            text = line["text"]

        keys = expand_target_keys(line.get("target_key", "*"))
        for key in keys:
            change: dict[str, Any] = {
                "Action": "EditData",
                "Target": f"Characters/Dialogue/{npc}",
                "Entries": {key: text},
                "LogName": f"{line_id}/{key}",
            }
            if when:
                change["When"] = {str(k): str(v) for k, v in when.items()}
                change["Update"] = "OnLocationChange,OnTimeChange"
            changes.append(change)

        # Follow-up dialogue entries are unconditional — they're only reached
        # via Stardew's chooseResponse path, so leaving them in the dict at
        # all times is safe and avoids load-order surprises.
        for rid, followup_text in followup_entries:
            changes.append({
                "Action": "EditData",
                "Target": f"Characters/Dialogue/{npc}",
                "Entries": {rid: followup_text},
                "LogName": f"{line_id}/followup/{rid}",
            })
    return {"Changes": changes}


def build_root(fragment_paths: list[str]) -> dict:
    return {
        "Format": CP_FORMAT,
        "Changes": [
            {"Action": "Include", "FromFile": f}
            for f in fragment_paths
        ],
    }


# ---------- main ----------

def main() -> int:
    if not SOURCE.exists():
        print(f"✗ {SOURCE} not found", file=sys.stderr)
        return 1

    INCLUDE.mkdir(parents=True, exist_ok=True)
    RESPONSES_OUT.parent.mkdir(parents=True, exist_ok=True)

    yaml_files = sorted(SOURCE.glob("*.yaml"))
    if not yaml_files:
        print(f"✗ No YAML files in {SOURCE}", file=sys.stderr)
        return 1

    lint_result = lint_all(yaml_files)
    if lint_result.errors:
        print("Lint errors — aborting build:", file=sys.stderr)
        for issue in lint_result.errors:
            print(f"  {issue}", file=sys.stderr)
        return 1
    if lint_result.warnings:
        print(f"Lint warnings ({len(lint_result.warnings)}):", file=sys.stderr)
        for issue in lint_result.warnings:
            print(f"  {issue}", file=sys.stderr)
        print(file=sys.stderr)

    fragment_paths: list[str] = []
    total_lines = 0
    total_changes = 0
    response_registry: dict[str, dict[str, dict[str, int]]] = {}

    for yaml_path in yaml_files:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        npc = data["npc"]
        lines = data["lines"]
        fragment = build_npc_fragment(npc, lines, response_registry)
        out_path = INCLUDE / f"{npc.lower()}.json"
        out_path.write_text(json.dumps(fragment, indent=2) + "\n", encoding="utf-8")
        rel = out_path.relative_to(OUT).as_posix()
        fragment_paths.append(rel)
        total_lines += len(lines)
        total_changes += len(fragment["Changes"])
        print(f"  · {npc}: {len(lines)} lines → {len(fragment['Changes'])} CP changes → {rel}")

    root = build_root(fragment_paths)
    (OUT / "content.json").write_text(json.dumps(root, indent=2) + "\n", encoding="utf-8")

    # Emit responses.json. The C# mod reads this from its mod folder; a
    # symlink in Mods/ECI.Tokens/ keeps it live across rebuilds.
    RESPONSES_OUT.write_text(
        json.dumps({"Responses": response_registry}, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"✓ Built {total_lines} lines → {total_changes} CP changes across {len(fragment_paths)} fragment(s)")
    print(f"  Root: {OUT / 'content.json'}")
    print(f"  Branching responses: {len(response_registry)} → {RESPONSES_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
