"""Kaggle GPU script: ACE-Step 1.5 instrumental cues, several candidates per cue.

Pushed and run by `pipeline/music.py`, which inserts the JOBS line below; do not run locally.
Runs ACE-Step's own cli.py with one TOML config per cue (thinking off: tempo, key and caption
come from storyboard.json). Writes <cue>_<n>.<ext> and music_log.jsonl to /kaggle/working.
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import time

JOBS = {}  # replaced by pipeline/music.py

OUT, WORK = "/kaggle/working", "/kaggle/temp"
REPO, CKPT = f"{WORK}/ACE-Step-1.5", f"{WORK}/checkpoints"
LOG = f"{OUT}/music_log.jsonl"


def log(**fields):
    with open(LOG, "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **fields}) + "\n")


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.returncode, (r.stdout + r.stderr)[-3000:]


def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    return json.dumps(v)  # a JSON string is a valid TOML basic string


t0 = time.time()
os.makedirs(WORK, exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "uv"], check=True)
code, out = run(["git", "clone", "--depth", "1", JOBS["repo"], REPO])
commit = run(["git", "-C", REPO, "rev-parse", "HEAD"])[1].strip()
code, out = run(["uv", "sync"], cwd=REPO)
log(event="setup", status="ok" if code == 0 else "error", commit=commit, setup_s=round(time.time() - t0, 1),
    tail=None if code == 0 else out)
env = {**os.environ, "ACESTEP_CHECKPOINTS_DIR": CKPT, "ACESTEP_PROJECT_ROOT": REPO}

for cue in JOBS["cues"]:
    save = f"{WORK}/out_{cue['id']}"
    cfg = {"project_root": REPO, "checkpoint_dir": CKPT, "config_path": JOBS["dit"], "save_dir": save,
           "backend": "pt", "device": "cuda", "task_type": "text2music", "thinking": False,
           "caption": cue["caption"], "lyrics": "[Instrumental]", "instrumental": True,
           "duration": cue["duration"], "bpm": cue["bpm"], "keyscale": cue["key"], "timesignature": "4",
           "inference_steps": 8, "shift": 3.0, "batch_size": len(cue["seeds"]),
           "use_random_seed": False, "seeds": cue["seeds"], "seed": cue["seeds"][0], "audio_format": "wav"}
    path = f"{WORK}/{cue['id']}.toml"
    with open(path, "w") as f:
        f.write("\n".join(f"{k} = {toml_value(v)}" for k, v in cfg.items()) + "\n")
    t = time.time()
    code, out = run(["uv", "run", "python", "cli.py", "--config", path, "--backend", "pt"], cwd=REPO, env=env)
    files = sorted(glob.glob(f"{save}/**/*.wav", recursive=True))
    saved = []
    for i, src in enumerate(files, 1):
        name = f"{cue['id']}_{i}.wav"
        shutil.copy(src, f"{OUT}/{name}")
        saved.append(name)
    log(event="cue", cue=cue["id"], status="ok" if code == 0 and saved else "error", latency_s=round(time.time() - t, 1),
        seeds=cue["seeds"], outputs=saved, tail=None if code == 0 and saved else out)
log(event="done", total_s=round(time.time() - t0, 1))
