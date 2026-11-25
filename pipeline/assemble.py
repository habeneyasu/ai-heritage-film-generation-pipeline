"""Stage: assembly (FFmpeg). Deterministic: no model calls.

    uv run python -m pipeline.assemble --radio-cut
Radio cut = narration over placeholder music on a black screen, with English
subtitles and the end card. Used for user test 1 (DESIGN.md section 8).
"""

import argparse
import json
import subprocess

from pipeline.common import ROOT
from pipeline.narration import MANIFEST
from pipeline.validate import load_storyboard

EDIT_DIR = ROOT / "outputs" / "edit"
LEAD_IN_S = 0.4   # pause at the start of a shot before the narrator speaks
MIN_GAP_S = 0.5   # minimum silence between two lines
W, H = 1280, 720


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def plan_timeline(sb: dict, manifest: dict) -> tuple[list[dict], float]:
    """Place each line at its shot start; push it later if the previous line is still playing."""
    events, shot_start, prev_end = [], 0.0, float("-inf")
    for shot in sb["shots"]:
        if shot["id"] in manifest:
            audio_s = manifest[shot["id"]]["audio_s"]
            start = max(shot_start + LEAD_IN_S, prev_end + MIN_GAP_S)
            events.append({"shot": shot["id"], "file": manifest[shot["id"]]["file"], "start": round(start, 2),
                           "end": round(start + audio_s, 2), "en": shot["narration"]["en"],
                           "drift": round(start - (shot_start + LEAD_IN_S), 2)})
            prev_end = start + audio_s
        shot_start += shot["duration_s"]
    total = max(shot_start, prev_end + MIN_GAP_S) + sb["end_card"]["duration_s"]
    return events, round(total, 2)


def radio_cut() -> None:
    sb = load_storyboard()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    missing = [s["id"] for s in sb["shots"] if s["narration"] and s["id"] not in manifest]
    if missing:
        raise SystemExit(f"Narration missing for {missing}; run: uv run python -m pipeline.narration")
    events, total = plan_timeline(sb, manifest)
    EDIT_DIR.mkdir(parents=True, exist_ok=True)

    # Subtitles: one cue per line, plus the end card.
    srt = EDIT_DIR / "radio_cut.srt"
    cues = [(e["start"], e["end"] + 0.3, e["en"]) for e in events]
    cues.append((total - sb["end_card"]["duration_s"], total, sb["end_card"]["text"]))
    srt.write_text("\n".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n" for i, (a, b, t) in enumerate(cues, 1)),
                   encoding="utf-8")

    # Audio: delayed narration lines -> voice bus; quiet A-minor drone as placeholder
    # music, ducked under the voice (sidechaincompress), then loudness-normalised.
    inputs, chains = [], []
    for i, e in enumerate(events):
        inputs += ["-i", e["file"]]
        ms = int(e["start"] * 1000)
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[n{i}]")
    n = len(events)
    music = (f"aevalsrc='0.04*(sin(2*PI*110*t)+0.6*sin(2*PI*164.81*t)+0.5*sin(2*PI*220*t))"
             f"*(0.8+0.2*sin(2*PI*0.1*t))':s=48000:d={total},aformat=channel_layouts=stereo,"
             f"afade=t=in:d=2,afade=t=out:st={total - 3}:d=3[music]")
    graph = ";".join(chains + [
        "".join(f"[n{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,apad,atrim=0:{total}[voice]",
        music,
        "[voice]asplit=2[vkey][vmix]",
        "[music][vkey]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[ducked]",
        "[vmix][ducked]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=11[aout]",
        f"color=c=black:s={W}x{H}:r={sb['fps']}:d={total},"
        f"subtitles={srt.relative_to(ROOT)}:force_style='FontSize=22,MarginV=40'[vout]",
    ])
    out = EDIT_DIR / "radio_cut.mp4"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
                    "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-ar", "48000", "-t", str(total), str(out.relative_to(ROOT))], cwd=ROOT, check=True)

    for e in events:
        note = f"  starts {e['drift']}s late (previous line still playing)" if e["drift"] > 0 else ""
        print(f"{e['shot']}  {e['start']:6.2f}s -> {e['end']:6.2f}s{note}")
    print(f"{out.relative_to(ROOT)}  {total}s total")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radio-cut", action="store_true", help="narration + placeholder music on black")
    args = ap.parse_args()
    if not args.radio_cut:
        raise SystemExit("Full assembly is not implemented yet; use --radio-cut.")
    radio_cut()
