"""Validate storyboard.json against the schema plus cross-field rules.

    uv run python -m pipeline.validate
Every stage calls load_storyboard(), so nothing runs on an invalid storyboard.
"""

import json
import sys

from jsonschema import Draft202012Validator

from pipeline.common import ROOT

STORYBOARD = ROOT / "storyboard.json"
SCHEMA = ROOT / "schema" / "storyboard.schema.json"
MIN_TOTAL_S, MAX_TOTAL_S = 60, 90


def check(sb: dict) -> list[str]:
    """Return a list of problems; empty means valid."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = [f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}"
              for e in Draft202012Validator(schema).iter_errors(sb)]
    if errors:
        return errors  # cross-field checks assume the shape is right

    ids = [s["id"] for s in sb["shots"]]
    if len(ids) != len(set(ids)):
        errors.append("shots: duplicate shot ids")
    if "reference_sheet" in sb:
        errors += [f"reference_sheet: unknown character '{c}'" for c in sb["reference_sheet"]["characters"]
                   if c not in sb["characters"]]
    errors += [f"characters/{k}: reference file not found: {c['reference']}" for k, c in sb["characters"].items()
               if "reference" in c and not (ROOT / c["reference"]).exists()]
    cues = {c["id"] for c in sb["music_cues"]}
    for s in sb["shots"]:
        errors += [f"shots/{s['id']}: unknown character '{c}'" for c in s["characters"] if c not in sb["characters"]]
        if s["music_cue"] not in cues:
            errors.append(f"shots/{s['id']}: unknown music cue '{s['music_cue']}'")
    total = sum(s["duration_s"] for s in sb["shots"]) + sb["end_card"]["duration_s"]
    if not MIN_TOTAL_S <= total <= MAX_TOTAL_S:
        errors.append(f"total duration {total}s is outside {MIN_TOTAL_S}-{MAX_TOTAL_S}s")
    return errors


def load_storyboard() -> dict:
    sb = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    errors = check(sb)
    if errors:
        raise SystemExit("storyboard.json is invalid:\n  " + "\n  ".join(errors))
    return sb


if __name__ == "__main__":
    sb = load_storyboard()
    total = sum(s["duration_s"] for s in sb["shots"]) + sb["end_card"]["duration_s"]
    narrated = sum(1 for s in sb["shots"] if s["narration"])
    print(f"storyboard.json is valid: {len(sb['shots'])} shots, {narrated} narrated, "
          f"{len(sb['music_cues'])} music cues, {total}s total")
    sys.exit(0)
