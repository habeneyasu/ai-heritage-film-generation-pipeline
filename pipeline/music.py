"""Stage: music (ACE-Step 1.5 on a Kaggle GPU), then the score for assembly.

    uv run python -m pipeline.music push    # generate candidates for every cue on Kaggle
    uv run python -m pipeline.music status
    uv run python -m pipeline.music pull    # download candidates to outputs/music/candidates/
    uv run python -m pipeline.music score   # chosen candidates -> outputs/music/score.wav

Each cue in storyboard.json covers the shots that name it; its length comes from the assembly
timeline. The author listens and sets "chosen" (1, 2 or 3) on each cue; `score` then joins the
chosen cues with crossfades at their shot boundaries. Assembly ducks the score under the voice.
"""

import argparse
import json
import shutil
import subprocess

from dotenv import load_dotenv

from pipeline.assemble import timeline
from pipeline.common import ROOT, log_call
from pipeline.validate import load_storyboard
from pipeline.wan import kaggle, username

OUT_DIR = ROOT / "outputs" / "music"
CANDIDATES = OUT_DIR / "candidates"
BUILD = ROOT / ".cache" / "kaggle_music"
SCRIPT = ROOT / "notebooks" / "music_cues.py"
KERNEL = "heritage-film-music"
REPO = "https://github.com/ace-step/ACE-Step-1.5.git"
CANDIDATES_PER_CUE = 3
XFADE_S = 3.0


def cue_spans(sb: dict) -> list[dict]:
    """Start and length of each cue on the film timeline (the last cue runs under the end card)."""
    shots, total = timeline(sb)
    cue_of = {s["id"]: s["music_cue"] for s in sb["shots"]}
    spans = []
    for s in shots:
        if spans and spans[-1]["id"] == cue_of[s["id"]]:
            spans[-1]["end"] = s["start"] + s["dur"]
        else:
            spans.append({"id": cue_of[s["id"]], "start": s["start"], "end": s["start"] + s["dur"]})
    spans[-1]["end"] = total
    return spans


def push() -> None:
    sb = load_storyboard()
    cues = {c["id"]: c for c in sb["music_cues"]}
    jobs = {"repo": REPO, "dit": "acestep-v15-turbo", "cues": []}
    for n, span in enumerate(cue_spans(sb)):
        c = cues[span["id"]]
        length = round(span["end"] - span["start"] + 2 * XFADE_S)  # room for the crossfades
        jobs["cues"].append({"id": c["id"], "caption": c["caption"], "bpm": c["bpm"], "key": c["key"],
                             "duration": max(10, length), "seeds": [300 + 10 * n + i for i in range(1, CANDIDATES_PER_CUE + 1)]})
    shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir(parents=True)
    script = SCRIPT.read_text().replace("JOBS = {}  # replaced by pipeline/music.py", f"JOBS = {json.dumps(jobs)}")
    (BUILD / SCRIPT.name).write_text(script)
    (BUILD / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{username()}/{KERNEL}", "title": KERNEL, "code_file": SCRIPT.name, "language": "python",
        "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True}))
    kaggle("kernels", "push", "-p", str(BUILD), "--accelerator", "NvidiaTeslaT4")
    for c in jobs["cues"]:
        print(f"{c['id']}: {c['duration']}s, {c['bpm']} bpm, {c['key']}, seeds {c['seeds']}")


def status() -> None:
    print(kaggle("kernels", "status", f"{username()}/{KERNEL}", capture=True).strip())


def pull() -> None:
    sb = load_storyboard()
    out = BUILD / "output"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    kaggle("kernels", "output", f"{username()}/{KERNEL}", "-p", str(out))
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    log_path = out / "music_log.jsonl"
    for e in (json.loads(x) for x in log_path.read_text().splitlines()) if log_path.exists() else []:
        if e["event"] != "cue":
            print(json.dumps({k: v for k, v in e.items() if k != "tail"}), "" if not e.get("tail") else "\n" + e["tail"][-800:])
            continue
        for name in e["outputs"]:
            shutil.copy(out / name, CANDIDATES / name)
        log_call(stage="music", model=sb["models"]["music"]["model"], params={"cue": e["cue"], "gpu": "Kaggle T4"},
                 seed=e["seeds"], attempt=1, latency_s=e["latency_s"], cost_usd=0.0, status=e["status"],
                 output=[f"outputs/music/candidates/{n}" for n in e["outputs"]], error=e.get("tail"))
        print(f"{e['cue']}: {e['status']} in {e['latency_s']}s -> {', '.join(e['outputs']) or 'nothing'}")


def score() -> None:
    """Join the chosen candidate of each cue, crossfading at the shot where the cue changes."""
    sb = load_storyboard()
    chosen = {c["id"]: c.get("chosen") for c in sb["music_cues"]}
    spans = cue_spans(sb)
    missing = [s["id"] for s in spans if not chosen[s["id"]]]
    if missing:
        raise SystemExit(f"Set \"chosen\" (1-{CANDIDATES_PER_CUE}) on music cues {missing} in storyboard.json")
    inputs, chains = [], []
    for i, s in enumerate(spans):
        inputs += ["-i", str(CANDIDATES / f"{s['id']}_{chosen[s['id']]}.wav")]
        start = max(0.0, s["start"] - (XFADE_S if i else 0))
        length = s["end"] - start + (XFADE_S if i < len(spans) - 1 else 0)
        fade_in = f"afade=t=in:d={XFADE_S}," if i else "afade=t=in:d=2,"
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{length:.2f},asetpts=PTS-STARTPTS,"
                      f"{fade_in}afade=t=out:st={length - XFADE_S:.2f}:d={XFADE_S},adelay={int(start * 1000)}|{int(start * 1000)}[c{i}]")
    graph = ";".join(chains) + ";" + "".join(f"[c{i}]" for i in range(len(spans))) + \
        f"amix=inputs={len(spans)}:normalize=0:duration=longest[out]"
    out = OUT_DIR / "score.wav"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", graph,
                    "-map", "[out]", "-ar", "48000", str(out)], cwd=ROOT, check=True)
    print(f"{out.relative_to(ROOT)}: " + ", ".join(f"{s['id']} #{chosen[s['id']]} {s['start']:.1f}-{s['end']:.1f}s" for s in spans))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["push", "status", "pull", "score"])
    args = ap.parse_args()
    load_dotenv()
    {"push": push, "status": status, "pull": pull, "score": score}[args.action]()
