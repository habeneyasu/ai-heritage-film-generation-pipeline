"""Stage: assembly (FFmpeg). Deterministic: no model calls.

    uv run python -m pipeline.assemble              # the film: 16:9 and 9:16, subtitles, end card
    uv run python -m pipeline.assemble --radio-cut  # narration + music on black (user test 1)

Timeline: each shot starts when the previous one ends. A narrated shot is lengthened when its
line is longer than the shot, so words and picture stay together ("narration sets the cut").
Audio: narration lines on the timeline, music ducked under the voice (sidechain), then two-pass
loudness normalisation to -14 LUFS. Video: each square shot clip is cropped to 16:9 and 9:16
(subjects are centred, DESIGN.md), English subtitles burned in, then the AI end card.
"""

import argparse
import json
import subprocess

from pipeline.common import ROOT
from pipeline.narration import OUT_DIR as NARRATION_DIR, duration_s, line_hash
from pipeline.shots import MANIFEST as SHOTS
from pipeline.validate import MAX_TOTAL_S, MIN_TOTAL_S, load_storyboard

EDIT_DIR = ROOT / "outputs" / "edit"
FINAL_DIR = ROOT / "outputs" / "final"
MUSIC_DIR = ROOT / "outputs" / "music"
LEAD_IN_S = 0.4   # pause at the start of a shot before the narrator speaks
TAIL_S = 0.8      # room after a line before the cut
LUFS, TRUE_PEAK, LRA = -14, -1, 11
MUSIC_GAIN_DB = -10  # the score sits this far under the voice before ducking (a music bed, not a co-lead)
FORMATS = {  # name: (width, height, subtitle size, subtitle margin in libass units)
    "16x9": (1920, 1080, 15, 18),
    "9x16": (1080, 1920, 10, 70),   # higher margin keeps text above the app UI
}


def crop_filter(name: str, shot: dict) -> str:
    """Cut the square clip; the storyboard's per-shot `crop` keeps the subject in frame (default centre)."""
    c = shot.get("crop", {})
    if name == "16x9":
        return f"crop=iw:iw*9/16:0:(ih-iw*9/16)*{c.get('y', 0.5)}"
    return f"crop=ih*9/16:ih:(iw-ih*9/16)*{c.get('x', 0.5)}:0"


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], cwd=ROOT, check=True)


def narration_file(sb: dict, shot: dict):
    """The current line for this shot (same hash as the narration stage), or None if not generated yet."""
    cfg = sb["models"]["narration"]
    text = (cfg["style"] + " " if cfg.get("style") else "") + shot["narration"]["ti"]
    path = NARRATION_DIR / f"{shot['id']}_{line_hash(cfg['model'], cfg['voice'], text)}.wav"
    return path if path.exists() else None


def timeline(sb: dict) -> tuple[list[dict], float]:
    """One entry per shot: start, duration and its narration line (if any)."""
    shots, t = [], 0.0
    for shot in sb["shots"]:
        line = narration_file(sb, shot) if shot["narration"] else None
        audio = duration_s(line) if line else 0.0
        dur = max(shot["duration_s"], round(LEAD_IN_S + audio + TAIL_S, 2)) if line else shot["duration_s"]
        shots.append({"id": shot["id"], "start": round(t, 2), "dur": dur, "planned": shot["duration_s"],
                      "line": line, "audio": audio, "en": shot["narration"]["en"] if shot["narration"] else None,
                      "missing": bool(shot["narration"]) and not line})
        t += dur
    return shots, round(t + sb["end_card"]["duration_s"], 2)


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def write_srt(sb: dict, shots: list, total: float, path) -> None:
    cues = [(s["start"] + LEAD_IN_S, s["start"] + LEAD_IN_S + s["audio"] + 0.3, s["en"]) for s in shots if s["line"]]
    cues.append((total - sb["end_card"]["duration_s"], total, sb["end_card"]["text"]))
    path.write_text("\n".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n" for i, (a, b, t) in enumerate(cues, 1)),
                    encoding="utf-8")


def music_input(sb: dict, total: float) -> tuple[list, str]:
    """Score from the music stage when it exists; otherwise a quiet A-minor drone as a placeholder."""
    track = MUSIC_DIR / "score.wav"
    if track.exists():
        return ["-i", str(track.relative_to(ROOT))], f"volume={MUSIC_GAIN_DB}dB,atrim=0:{total},afade=t=out:st={total - 3}:d=3"
    return [], (f"aevalsrc='0.04*(sin(2*PI*110*t)+0.6*sin(2*PI*164.81*t)+0.5*sin(2*PI*220*t))"
                f"*(0.8+0.2*sin(2*PI*0.1*t))':s=48000:d={total},afade=t=in:d=2,afade=t=out:st={total - 3}:d=3")


def mix_audio(sb: dict, shots: list, total: float, out) -> None:
    """Narration + ducked music, then two-pass loudnorm to -14 LUFS."""
    lines = [s for s in shots if s["line"]]
    inputs, chains = [], []
    for i, s in enumerate(lines):
        inputs += ["-i", str(s["line"].relative_to(ROOT))]
        ms = int((s["start"] + LEAD_IN_S) * 1000)
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[n{i}]")
    music_args, music_filter = music_input(sb, total)
    m = len(lines)
    music_src = f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,{music_filter}[music]" if music_args \
        else f"{music_filter},aformat=channel_layouts=stereo[music]"
    graph = ";".join(chains + [
        "".join(f"[n{i}]" for i in range(m)) + f"amix=inputs={m}:normalize=0:duration=longest,apad,atrim=0:{total}[voice]",
        music_src,
        "[voice]asplit=2[vkey][vmix]",
        "[music][vkey]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[ducked]",
        "[vmix][ducked]amix=inputs=2:normalize=0[aout]",
    ])
    raw = EDIT_DIR / "mix_raw.wav"
    ffmpeg(*inputs, *music_args, "-filter_complex", graph, "-map", "[aout]", "-ar", "48000", "-t", str(total), str(raw))
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af",
                            f"loudnorm=I={LUFS}:TP={TRUE_PEAK}:LRA={LRA}:print_format=json", "-f", "null", "-"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stderr
    m1 = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    ffmpeg("-i", str(raw), "-af",
           f"loudnorm=I={LUFS}:TP={TRUE_PEAK}:LRA={LRA}:measured_I={m1['input_i']}:measured_TP={m1['input_tp']}:"
           f"measured_LRA={m1['input_lra']}:measured_thresh={m1['input_thresh']}:offset={m1['target_offset']}:linear=true",
           "-ar", "48000", str(out))


def render_video(sb: dict, shots: list, total: float, audio, srt, name: str) -> None:
    w, h, font, margin = FORMATS[name]
    clips = json.loads(SHOTS.read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in sb["shots"]}
    inputs, chains = [], []
    for i, s in enumerate(shots):
        inputs += ["-i", clips[s["id"]]["file"]]
        chains.append(f"[{i}:v]setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={s['dur']},"
                      f"trim=duration={s['dur']},fps={sb['fps']},{crop_filter(name, by_id[s['id']])},scale={w}:{h}:flags=lanczos,setsar=1[v{i}]")
    n, card = len(shots), sb["end_card"]["duration_s"]
    pictures = total - card
    graph = ";".join(chains + [
        "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,fade=t=in:d=0.8,fade=t=out:st={pictures - 0.8}:d=0.8[pics]",
        f"color=c=black:s={w}x{h}:r={sb['fps']}:d={card}[card]",
        "[pics][card]concat=n=2:v=1:a=0,format=yuv420p,"
        f"subtitles={srt.relative_to(ROOT)}:force_style='FontName=DejaVu Sans,FontSize={font},MarginV={margin},"
        f"Outline=1.5,Shadow=0.5'[vout]",
    ])
    out = FINAL_DIR / f"heritage_{name}.mp4"
    ffmpeg(*inputs, "-i", str(audio.relative_to(ROOT)), "-filter_complex", graph, "-map", "[vout]", "-map", f"{n}:a",
           "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-t", str(total), str(out.relative_to(ROOT)))
    print(f"{out.relative_to(ROOT)}  {w}x{h}")


def report(shots: list, total: float) -> None:
    for s in shots:
        note = "  NARRATION MISSING (draft)" if s["missing"] else (
            f"  lengthened {s['planned']}s -> {s['dur']}s for the line" if s["dur"] > s["planned"] else "")
        print(f"{s['id']}  {s['start']:6.2f}s  {s['dur']:5.2f}s{note}")
    ok = MIN_TOTAL_S <= total <= MAX_TOTAL_S
    print(f"total {total}s {'(within' if ok else '(OUTSIDE'} {MIN_TOTAL_S}-{MAX_TOTAL_S}s)")


def film() -> None:
    sb = load_storyboard()
    shots, total = timeline(sb)
    report(shots, total)
    EDIT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    srt = FINAL_DIR / "heritage_en.srt"
    write_srt(sb, shots, total, srt)
    audio = EDIT_DIR / "mix.wav"
    mix_audio(sb, shots, total, audio)
    for name in FORMATS:
        render_video(sb, shots, total, audio, srt, name)


def radio_cut() -> None:
    """Narration and music on black with subtitles: the audio animatic for user test 1."""
    sb = load_storyboard()
    shots, total = timeline(sb)
    report(shots, total)
    EDIT_DIR.mkdir(parents=True, exist_ok=True)
    srt = EDIT_DIR / "radio_cut.srt"
    write_srt(sb, shots, total, srt)
    audio = EDIT_DIR / "mix.wav"
    mix_audio(sb, shots, total, audio)
    out = EDIT_DIR / "radio_cut.mp4"
    ffmpeg("-f", "lavfi", "-i", f"color=c=black:s=1280x720:r={sb['fps']}:d={total}", "-i", str(audio.relative_to(ROOT)),
           "-vf", f"subtitles={srt.relative_to(ROOT)}:force_style='FontSize=22,MarginV=40'",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(total),
           str(out.relative_to(ROOT)))
    print(f"{out.relative_to(ROOT)}  {total}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radio-cut", action="store_true", help="narration + music on black (user test 1)")
    radio_cut() if ap.parse_args().radio_cut else film()
