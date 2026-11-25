"""Stage: narration (Gemini TTS), one WAV per shot from storyboard.json.

    uv run python -m pipeline.narration            # all shots, cached by input hash
    uv run python -m pipeline.narration --sample   # the early Tigrigna check (EXPERIMENTS.md E01)

Writes outputs/narration/<shot>_<hash>.wav and outputs/narration/manifest.json,
which the assembly stage reads.
"""

import argparse
import hashlib
import json
import subprocess
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from pipeline.common import ROOT, QuotaExhausted, call_logged, log_call
from pipeline.validate import load_storyboard

OUT_DIR = ROOT / "outputs" / "narration"
MANIFEST = OUT_DIR / "manifest.json"
PACE_S = 4  # pause between paid-for-nothing calls to stay under the free-tier rate limit (FAILURES.md F02)

# --- Early Tigrigna check (kept so E01 stays reproducible) ---------------------
SAMPLE_DIR = OUT_DIR / "samples"
SAMPLE_MODEL, SAMPLE_API, SAMPLE_VOICE = "gemini-3.8-flash-tts", "v1beta", "Sulafat"
SAMPLE_STYLE = "Read in Tigrinya, slowly and warmly, like an elder telling a family story: "
SAMPLES = [  # (file id, Tigrigna text, use style instruction)
    ("s1_tesfay_hawey", "ተስፋይ ሓወይ!", False),
    ("s2_weldechael_hawey", "ወልደቻኣል ሓወይ!", False),
    ("s3_opening_plain", "ኣብ ሓንቲ ዓዲ ዶግዓ ትግራይ፡ ወልደቻኣልን ተስፋይን ዝበሃሉ ክልተ ኣሕዋት ይነብሩ ነበሩ።", False),
    ("s3_opening_styled", "ኣብ ሓንቲ ዓዲ ዶግዓ ትግራይ፡ ወልደቻኣልን ተስፋይን ዝበሃሉ ክልተ ኣሕዋት ይነብሩ ነበሩ።", True),
]


def duration_s(path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return round(float(out.stdout.strip() or 0), 2)


def synthesize(client, model: str, text: str, voice: str) -> bytes:
    cfg = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))))
    r = client.models.generate_content(model=model, contents=text, config=cfg)
    return r.candidates[0].content.parts[0].inline_data.data


def generate(client, *, model, api_version, voice, text, path, stage, extra=None) -> dict:
    """Generate one line unless its hashed file already exists. Returns a manifest entry."""
    if path.exists():
        return {"file": str(path.relative_to(ROOT)), "audio_s": duration_s(path), "cached": True}
    audio, entry = call_logged(lambda: synthesize(client, model, text, voice),
                               stage=stage, model=model, attempts=4, backoff_s=10,
                               params={"voice": voice, "text": text, "api_version": api_version, **(extra or {})})
    path.write_bytes(audio)
    entry.update(output=str(path.relative_to(ROOT)), audio_s=duration_s(path))
    log_call(**entry)
    time.sleep(PACE_S)
    return {"file": str(path.relative_to(ROOT)), "audio_s": entry["audio_s"], "cached": False}


def line_hash(model: str, voice: str, text: str) -> str:
    return hashlib.sha256(f"{model}|{voice}|{text}".encode()).hexdigest()[:8]


def run_storyboard() -> None:
    sb = load_storyboard()
    cfg = sb["models"]["narration"]
    client = genai.Client(http_options=types.HttpOptions(api_version=cfg["api_version"]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for shot in sb["shots"]:
        if not shot["narration"]:
            continue
        text = (cfg["style"] + " " if cfg.get("style") else "") + shot["narration"]["ti"]
        path = OUT_DIR / f"{shot['id']}_{line_hash(cfg['model'], cfg['voice'], text)}.wav"
        try:
            item = generate(client, model=cfg["model"], api_version=cfg["api_version"], voice=cfg["voice"],
                            text=text, path=path, stage="narration", extra={"shot": shot["id"]})
        except QuotaExhausted as e:
            MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            raise SystemExit(f"Stopped at {shot['id']}: {e}. Lines done so far are saved; re-run later.")
        manifest[shot["id"]] = {k: item[k] for k in ("file", "audio_s")}
        fit = "OK" if item["audio_s"] <= shot["duration_s"] else "LONGER THAN SHOT"
        print(f"{shot['id']}  {item['audio_s']:5.2f}s speech / {shot['duration_s']}s shot  "
              f"{'cached' if item['cached'] else 'generated'}  {fit}")
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_sample() -> None:
    client = genai.Client(http_options=types.HttpOptions(api_version=SAMPLE_API))
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    for sid, text, styled in SAMPLES:
        prompt = SAMPLE_STYLE + text if styled else text
        path = SAMPLE_DIR / f"{sid}_{SAMPLE_VOICE}_{line_hash(SAMPLE_MODEL, SAMPLE_VOICE, prompt)}.wav"
        item = generate(client, model=SAMPLE_MODEL, api_version=SAMPLE_API, voice=SAMPLE_VOICE,
                        text=prompt, path=path, stage="narration-sample", extra={"styled": styled})
        print(f"{item['file']}  {item['audio_s']}s  {'cached' if item['cached'] else 'generated'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="regenerate the early Tigrigna check")
    args = ap.parse_args()
    load_dotenv()
    run_sample() if args.sample else run_storyboard()
