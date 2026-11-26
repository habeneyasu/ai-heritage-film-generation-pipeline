"""Stage helper: Wan 2.2 clips on a Kaggle GPU (T4), driven from here.

    uv run python -m pipeline.wan push --shots s09   # upload keyframes + jobs, start the GPU run
    uv run python -m pipeline.wan status             # is it still running?
    uv run python -m pipeline.wan pull               # download clips to outputs/shots/wan/, log to runs.jsonl

Settings come from storyboard.json ("models.shots"). Each clip's file name is a hash of its
inputs, so `push` skips shots whose current clip already exists and `pipeline.shots` only uses a
clip that matches the current keyframe and prompt. Needs KAGGLE_API_TOKEN in .env.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time

from dotenv import load_dotenv

from pipeline.common import ROOT, log_call
from pipeline.keyframes import MANIFEST as KEYFRAMES
from pipeline.validate import load_storyboard

WAN_DIR = ROOT / "outputs" / "shots" / "wan"
BUILD = ROOT / ".cache" / "kaggle"  # git-ignored staging folders for upload
SCRIPT = ROOT / "notebooks" / "wan_shots.py"
DATASET, KERNEL = "heritage-film-keyframes", "heritage-film-wan"
NEGATIVE = ("text, subtitles, watermark, modern objects, lamps, fast motion, camera shake, morphing faces, "
            "deformed hands, extra fingers, extra people, blurry, low quality, overexposed, static frame")


def kaggle(*args: str, capture: bool = False) -> str:
    r = subprocess.run(["kaggle", *args], cwd=ROOT, capture_output=capture, text=True)
    if r.returncode != 0:
        raise SystemExit(f"kaggle {' '.join(args)} failed:\n{r.stderr if capture else ''}")
    return r.stdout if capture else ""


def accelerator() -> str:
    """Kaggle GPU type; KAGGLE_ACCELERATOR in .env overrides the free-tier default (2× Tesla T4)."""
    return os.environ.get("KAGGLE_ACCELERATOR", "NvidiaTeslaT4")


def username() -> str:
    out = kaggle("config", "view", capture=True)
    return next(line.split(":", 1)[1].strip() for line in out.splitlines() if "username" in line)


def job_for(sb: dict, shot: dict, keyframe) -> dict:
    cfg = sb["models"]["shots"]
    job = {"shot": shot["id"], "prompt": f"{shot['motion_prompt']} {shot['image_prompt']}",
           "width": cfg["width"], "height": cfg["height"], "frames": cfg["frames"], "steps": cfg["steps"],
           "guidance": cfg["guidance"], "fps": sb["fps"], "seed": shot["seed"]}
    key = json.dumps({**job, "model": cfg["model"], "negative": NEGATIVE,
                      "keyframe": hashlib.sha256(keyframe.read_bytes()).hexdigest()}, sort_keys=True)
    job["output"] = f"{shot['id']}_{hashlib.sha256(key.encode()).hexdigest()[:8]}.mp4"
    return job


def current_clip(sb: dict, shot: dict, keyframe):
    """The Wan clip for this exact keyframe and prompt, if it has been generated."""
    path = WAN_DIR / job_for(sb, shot, keyframe)["output"]
    return path if path.exists() else None


def push(only: set[str]) -> None:
    sb = load_storyboard()
    keyframes = json.loads(KEYFRAMES.read_text(encoding="utf-8"))
    user = username()
    data, code = BUILD / "dataset", BUILD / "kernel"
    shutil.rmtree(BUILD, ignore_errors=True)
    data.mkdir(parents=True)
    code.mkdir(parents=True)
    jobs = []
    for shot in sb["shots"]:
        if shot["id"] not in only:
            continue
        keyframe = ROOT / keyframes[shot["id"]]
        job = job_for(sb, shot, keyframe)
        if (WAN_DIR / job["output"]).exists():
            print(f"{shot['id']}: clip exists, skipped")
            continue
        shutil.copy(keyframe, data / f"{shot['id']}.jpg")
        jobs.append({**job, "image": f"{shot['id']}.jpg"})
    if not jobs:
        return print("Nothing to generate.")
    (data / "jobs.json").write_text(json.dumps({"model": sb["models"]["shots"]["model"], "negative_prompt": NEGATIVE,
                                                "jobs": jobs}, indent=2), encoding="utf-8")
    (data / "dataset-metadata.json").write_text(json.dumps(
        {"title": DATASET, "id": f"{user}/{DATASET}", "licenses": [{"name": "CC0-1.0"}]}), encoding="utf-8")
    exists = subprocess.run(["kaggle", "datasets", "status", f"{user}/{DATASET}"], cwd=ROOT,
                            capture_output=True, text=True).returncode == 0
    kaggle(*(["datasets", "version", "-p", str(data), "-m", "keyframes and jobs"] if exists
             else ["datasets", "create", "-p", str(data)]))
    for _ in range(30):  # the kernel must see the new version, so wait until it is processed
        if "ready" in kaggle("datasets", "status", f"{user}/{DATASET}", capture=True).lower():
            break
        time.sleep(10)
    shutil.copy(SCRIPT, code / SCRIPT.name)
    (code / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{user}/{KERNEL}", "title": KERNEL, "code_file": SCRIPT.name, "language": "python",
        "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
        "dataset_sources": [f"{user}/{DATASET}"]}), encoding="utf-8")
    kaggle("kernels", "push", "-p", str(code), "--accelerator", accelerator())
    print(f"Started {len(jobs)} clip(s): {', '.join(j['shot'] for j in jobs)}. Check with: python -m pipeline.wan status")


def status() -> None:
    print(kaggle("kernels", "status", f"{username()}/{KERNEL}", capture=True).strip())


def pull() -> None:
    sb = load_storyboard()
    out = BUILD / "output"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    kaggle("kernels", "output", f"{username()}/{KERNEL}", "-p", str(out))
    WAN_DIR.mkdir(parents=True, exist_ok=True)
    log_path = out / "wan_log.jsonl"
    entries = [json.loads(line) for line in log_path.read_text().splitlines()] if log_path.exists() else []
    for e in entries:
        if e.get("event") != "clip":
            print(json.dumps(e))
            continue
        src = out / e["output"]
        if e["status"] == "ok" and src.exists():
            shutil.copy(src, WAN_DIR / e["output"])
        log_call(stage="shots", model=sb["models"]["shots"]["model"], params={"shot": e["shot"], "gpu": "Kaggle T4"},
                 seed=None, attempt=1, latency_s=e["latency_s"], cost_usd=0.0, status=e["status"],
                 output=f"outputs/shots/wan/{e['output']}" if e["status"] == "ok" else None,
                 peak_gpu_gb=e.get("peak_gpu_gb"), error=e.get("error"))
        print(f"{e['shot']}: {e['status']} in {e['latency_s']}s" + (f", peak {e['peak_gpu_gb']} GB" if e.get("peak_gpu_gb") else "")
              + (f"\n  {e['error']}" if e.get("error") else ""))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["push", "status", "pull"])
    ap.add_argument("--shots", help="comma-separated shot ids for push")
    args = ap.parse_args()
    load_dotenv()
    if args.action == "push":
        if not args.shots:
            raise SystemExit("push needs --shots, e.g. --shots s09")
        push(set(args.shots.split(",")))
    else:
        {"status": status, "pull": pull}[args.action]()
