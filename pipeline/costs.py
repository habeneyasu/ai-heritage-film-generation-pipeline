"""Summarise runs.jsonl per stage and model: calls, failures, time and money.

    uv run python -m pipeline.costs   # prints the Markdown table used in COSTS.md
"""

import collections
import json

from pipeline.common import RUNS


def summary() -> str:
    rows = collections.defaultdict(lambda: {"ok": 0, "error": 0, "seconds": 0.0, "usd": 0.0})
    for line in RUNS.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        row = rows[(r["stage"], r["model"])]
        row["ok" if r["status"] == "ok" else "error"] += 1
        row["seconds"] += r.get("latency_s") or 0
        row["usd"] += r.get("cost_usd") or 0
    out = ["| Stage | Model | Calls OK | Failed | Model time | Cost (USD) |", "|---|---|---|---|---|---|"]
    for (stage, model), v in sorted(rows.items()):
        out.append(f"| {stage} | `{model}` | {v['ok']} | {v['error']} | {v['seconds'] / 60:.1f} min | {v['usd']:.2f} |")
    t = {k: sum(v[k] for v in rows.values()) for k in ("ok", "error", "seconds", "usd")}
    out.append(f"| **Total** | | **{t['ok']}** | **{t['error']}** | **{t['seconds'] / 60:.1f} min** | **{t['usd']:.2f}** |")
    return "\n".join(out)


if __name__ == "__main__":
    print(summary())
