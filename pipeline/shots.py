"""Stage: moving shots, one clip per shot from its keyframe.

    uv run python -m pipeline.shots                  # all shots, cached by input hash
    uv run python -m pipeline.shots --shots s01,s09  # only these shots

Each shot uses its Wan 2.2 clip when one matches the current keyframe and prompt (made on a
Kaggle GPU by pipeline/wan.py). Wan clips are about 3.4 s, so they are slowed to the shot length
with motion interpolation. Otherwise the storyboard's `fallback` camera move animates the
keyframe (FFmpeg, no model call): a slow push-in, pull-out or pan, as the challenge allows.
Clips are square like the keyframes, so assembly can crop both 16:9 and 9:16 from them.
Writes outputs/shots/<shot>_<hash>.mp4 and outputs/shots/manifest.json.
"""

import argparse
import hashlib
import json
import subprocess

from pipeline.common import ROOT
from pipeline.keyframes import MANIFEST as KEYFRAMES
from pipeline.wan import current_clip
from pipeline.validate import load_storyboard

OUT_DIR = ROOT / "outputs" / "shots"
WAN_DIR = OUT_DIR / "wan"
MANIFEST = OUT_DIR / "manifest.json"
SIZE = 1024       # output square, same as the keyframes
WORK = 4          # zoompan works on an image this many times larger, to avoid jitter

def moves(zoom: float) -> dict:
    """Zoom and top-left x as functions of T (0 -> 1); y keeps the frame centred. `zoom` comes from storyboard.json."""
    return {"kenburns-in": (f"1+{zoom - 1}*T", "(iw-iw/zoom)/2"),
            "kenburns-out": (f"{zoom}-{zoom - 1}*T", "(iw-iw/zoom)/2"),
            "pan-left": (f"{zoom}", "(iw-iw/zoom)*(1-T)"),
            "pan-right": (f"{zoom}", "(iw-iw/zoom)*T")}


def fallback_clip(keyframe, move: str, duration: float, fps: int, zoom: float, out) -> None:
    frames = round(duration * fps)
    t = f"(on/{max(frames - 1, 1)})"
    z, x = (expr.replace("T", t) for expr in moves(zoom)[move])
    vf = (f"scale={SIZE * WORK}:{SIZE * WORK},"
          f"zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':d={frames}:s={SIZE}x{SIZE}:fps={fps},"
          f"format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(keyframe), "-vf", vf,
                    "-frames:v", str(frames), "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)],
                   check=True)


def clip_seconds(path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def conform_wan(clip, duration: float, fps: int, out) -> None:
    """Slow the Wan clip to the shot length; motion interpolation keeps the slow motion smooth."""
    factor = duration / clip_seconds(clip)
    vf = (f"setpts={factor:.4f}*PTS,minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
          f"scale={SIZE}:{SIZE}:flags=lanczos,format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(clip), "-vf", vf,
                    "-t", str(duration), "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)], check=True)


def run(only: set[str] | None) -> None:
    sb = load_storyboard()
    keyframes = json.loads(KEYFRAMES.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    for shot in sb["shots"]:
        if only and shot["id"] not in only:
            continue
        keyframe = ROOT / keyframes[shot["id"]]
        wan = current_clip(sb, shot, keyframe)
        if wan:
            out = OUT_DIR / f"{wan.stem}_{shot['duration_s']}s.mp4"
            cached = out.exists()
            if not cached:
                conform_wan(wan, shot["duration_s"], sb["fps"], out)
            manifest[shot["id"]] = {"file": str(out.relative_to(ROOT)), "source": f"wan:{wan.name}"}
            print(f"{shot['id']}  {out.relative_to(ROOT)}  (wan, {'cached' if cached else 'conformed'})")
            continue
        move = shot.get("fallback", "kenburns-in")
        key = f"{hashlib.sha256(keyframe.read_bytes()).hexdigest()[:16]}|{move}|{shot['duration_s']}|{sb['fps']}|{SIZE}|{sb['edit']['camera_move_zoom']}"
        out = OUT_DIR / f"{shot['id']}_{hashlib.sha256(key.encode()).hexdigest()[:8]}.mp4"
        cached = out.exists()
        if not cached:
            fallback_clip(keyframe, move, shot["duration_s"], sb["fps"], sb["edit"]["camera_move_zoom"], out)
        manifest[shot["id"]] = {"file": str(out.relative_to(ROOT)), "source": f"fallback:{move}"}
        print(f"{shot['id']}  {out.relative_to(ROOT)}  ({move}, {'cached' if cached else 'rendered'})")
    order = [s["id"] for s in sb["shots"]]
    manifest = {k: manifest[k] for k in order if k in manifest}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", help="comma-separated shot ids (default: all)")
    args = ap.parse_args()
    run(set(args.shots.split(",")) if args.shots else None)
