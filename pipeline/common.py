"""Shared helpers: one runs.jsonl line per model call, with retries."""

import datetime
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs.jsonl"


def log_call(**fields) -> None:
    """Append one JSON line to runs.jsonl."""
    entry = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), **fields}
    with RUNS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def call_logged(fn, *, stage, model, params, seed=None, cost_usd=0.0, attempts=3, backoff_s=2.0):
    """Run fn() with retries; log every attempt (success or error) to runs.jsonl."""
    for attempt in range(1, attempts + 1):
        start = time.perf_counter()
        try:
            result = fn()
        except Exception as e:  # noqa: BLE001 - every failure is logged, then retried
            log_call(stage=stage, model=model, params=params, seed=seed, attempt=attempt,
                     latency_s=round(time.perf_counter() - start, 2), cost_usd=0.0,
                     status="error", error=str(e)[:300])
            if attempt == attempts:
                raise
            time.sleep(backoff_s * attempt)
        else:
            latency = round(time.perf_counter() - start, 2)
            return result, dict(stage=stage, model=model, params=params, seed=seed,
                                attempt=attempt, latency_s=latency, cost_usd=cost_usd, status="ok")
