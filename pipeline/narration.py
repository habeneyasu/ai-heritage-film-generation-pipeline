"""Stage: narration (Gemini TTS).

For now only the early Tigrinya check (DESIGN.md section 7):
    uv run python -m pipeline.narration --sample
"""

import argparse
import hashlib
import subprocess

from dotenv import load_dotenv
from google import genai
from google.genai import types

from pipeline.common import ROOT, call_logged, log_call

MODEL = "gemini-3.8-flash-tts"   # not shown by models.list(); needs the v1beta API
API_VERSION = "v1beta"
DEFAULT_VOICE = "Sulafat"        # described as "warm"
STYLE = "Read in Tigrinya, slowly and warmly, like an elder telling a family story: "

SAMPLE_DIR = ROOT / "outputs" / "narration" / "samples"

# (file id, Tigrinya text, use style instruction, English meaning for the subtitle check)
SAMPLES = [
    ("s1_tesfay_hawey", "ተስፋይ ሓወይ!", False, "My brother, Tesfay!"),
    ("s2_weldechael_hawey", "ወልደቻኣል ሓወይ!", False, "My brother, Weldechael!"),
    ("s3_opening_plain", "ኣብ ሓንቲ ዓዲ ዶግዓ ትግራይ፡ ወልደቻኣልን ተስፋይን ዝበሃሉ ክልተ ኣሕዋት ይነብሩ ነበሩ።", False,
     "In a highland village in Tigray, there lived two brothers, Weldechael and Tesfay."),
    ("s3_opening_styled", "ኣብ ሓንቲ ዓዲ ዶግዓ ትግራይ፡ ወልደቻኣልን ተስፋይን ዝበሃሉ ክልተ ኣሕዋት ይነብሩ ነበሩ።", True,
     "In a highland village in Tigray, there lived two brothers, Weldechael and Tesfay."),
]


def duration_s(path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return round(float(out.stdout.strip() or 0), 2)


def synthesize(client, text: str, voice: str) -> bytes:
    cfg = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))))
    r = client.models.generate_content(model=MODEL, contents=text, config=cfg)
    return r.candidates[0].content.parts[0].inline_data.data


def run_sample(voice: str) -> None:
    load_dotenv()
    client = genai.Client(http_options=types.HttpOptions(api_version=API_VERSION))
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    for sid, text, styled, english in SAMPLES:
        prompt = STYLE + text if styled else text
        key = hashlib.sha256(f"{MODEL}|{voice}|{prompt}".encode()).hexdigest()[:8]
        path = SAMPLE_DIR / f"{sid}_{voice}_{key}.wav"
        if path.exists():
            print(f"{path.relative_to(ROOT)}  cached, skipped")
            continue
        audio, entry = call_logged(lambda: synthesize(client, prompt, voice),
                                   stage="narration-sample", model=MODEL,
                                   params={"voice": voice, "styled": styled, "text": text,
                                           "api_version": API_VERSION})
        path.write_bytes(audio)
        entry.update(output=str(path.relative_to(ROOT)), audio_s=duration_s(path))
        log_call(**entry)
        print(f"{path.relative_to(ROOT)}  {entry['audio_s']}s audio, {entry['latency_s']}s latency  | {english}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="generate the Tigrinya check samples")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    args = ap.parse_args()
    if not args.sample:
        raise SystemExit("Full narration is not implemented yet; use --sample.")
    run_sample(args.voice)
