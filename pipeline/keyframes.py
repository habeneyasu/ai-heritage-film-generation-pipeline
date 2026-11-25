"""Stage: keyframes (FLUX.2 klein on Cloudflare Workers AI), one image per shot from storyboard.json.

    uv run python -m pipeline.keyframes                  # all shots, cached by input hash
    uv run python -m pipeline.keyframes --shots s01,s04  # only these shots

Two passes per shot (EXPERIMENTS.md E04):
1. Scene: shot scene + each character's full description + the fixed style block, text only.
   This gets the setting, the other people, the poses and the framing right.
2. Identity: for shots with a character who has an approved reference portrait, an edit call
   keeps the scene image and makes each brother match his portrait. Inserts (hands) skip it.
Writes outputs/keyframes/scenes/<shot>_<hash>.jpg, outputs/keyframes/<shot>_<hash>.jpg and
outputs/keyframes/manifest.json, which the shots stage reads. Every file name is a hash of its
inputs, so a re-run only calls the model for what changed.
"""

import argparse
import base64
import hashlib
import json
import os
import pathlib

import subprocess

import requests
from dotenv import load_dotenv

from pipeline.common import ROOT, call_logged, log_call
from pipeline.validate import load_storyboard

OUT_DIR = ROOT / "outputs" / "keyframes"
SCENE_DIR = OUT_DIR / "scenes"
MANIFEST = OUT_DIR / "manifest.json"
MAX_PROMPT = 2048  # Workers AI FLUX prompt limit
NO_IDENTITY_PASS = {"insert"}  # shot sizes where the brothers' faces are not shown


def cap(text: str) -> str:
    return text[0].upper() + text[1:]


def face_crop(char_id: str, c: dict):
    """Head-and-shoulders crop of the approved portrait (FFmpeg, no model call), cached by crop box."""
    x, y, w, h = c["face_crop"]
    path = SCENE_DIR.parent / "faces" / f"{char_id}_{x}_{y}_{w}_{h}_{pathlib.Path(c['reference']).stem}.jpg"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(ROOT / c["reference"]),
                        "-vf", f"crop={w}:{h}:{x}:{y}", "-q:v", "2", str(path)], check=True)
    return path


def references(sb: dict, shot: dict) -> list:
    """(role, portrait path, carries a stick) for characters in this shot with an approved reference.
    Close-ups use the face crop, so the model does not copy the full-length pose."""
    close = shot["size"] == "close-up"
    return [(c["role"], face_crop(k, c) if close and c.get("face_crop") else ROOT / c["reference"],
             "walking stick" in c["description"])
            for k, c in ((k, sb["characters"][k]) for k in shot["characters"]) if c.get("reference")]


def scene_prompt(sb: dict, shot: dict) -> str:
    def text(c: dict) -> str:  # full dress makes the model frame the whole body, so close-ups get face and gabi only
        return c.get("close_up", c["description"]) if shot["size"] == "close-up" else c["description"]
    chars = [f"{cap(sb['characters'][c]['role'])}: {text(sb['characters'][c])}." for c in shot["characters"]]
    return checked(shot, " ".join([shot["image_prompt"], *chars, sb["style_block"]]))


def identity_prompt(shot: dict, refs: list) -> str:
    """Image 1 is the scene; images 2, 3, ... are the portraits, in the order of `refs`."""
    close = shot["size"] == "close-up"
    swaps = " ".join(f"{cap(role)} must look exactly like the man in image {i + 2}: same face, hair, beard"
                     + (" and gabi." if close else ", clothing and footwear"
                        + (", holding his walking stick." if stick else "; he carries no walking stick."))
                     for i, (role, _, stick) in enumerate(refs))
    return checked(shot, "Keep image 1 exactly: the same scene, setting, composition, camera framing, poses, light and "
                         f"all other people. Change only the brothers. {swaps} Do not copy the backgrounds of the other images.")


def checked(shot: dict, prompt: str) -> str:
    if len(prompt) > MAX_PROMPT:
        raise SystemExit(f"{shot['id']}: prompt is {len(prompt)} characters; the model accepts {MAX_PROMPT}")
    return prompt


def render(cfg: dict, prompt: str, seed: int, images: list = ()) -> bytes:
    """FLUX.2 klein takes multipart form fields (flux-1-schnell rejected `seed`, EXPERIMENTS.md E03);
    input images go in input_image_0, input_image_1, ..."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/run/{cfg['model']}"
    fields = {"prompt": prompt, "seed": seed, "width": cfg["width"], "height": cfg["height"], "steps": cfg["steps"]}
    files = {k: (None, str(v)) for k, v in fields.items()}
    files.update({f"input_image_{i}": (path.name, path.read_bytes(), "image/jpeg") for i, path in enumerate(images)})
    r = requests.post(url, headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"},
                      files=files, timeout=180)
    if not r.ok:
        raise RuntimeError(f"{r.status_code} {r.text[:500]}")
    return base64.b64decode(r.json()["result"]["image"])


def key_hash(cfg: dict, seed: int, prompt: str, images: list = ()) -> str:
    """Everything that changes the image, including the input images' contents."""
    image_ids = ",".join(hashlib.sha256(path.read_bytes()).hexdigest()[:16] for path in images)
    key = f"{cfg['model']}|{cfg['width']}x{cfg['height']}|{cfg['steps']}|{seed}|{prompt}|{image_ids}"
    return hashlib.sha256(key.encode()).hexdigest()[:8]


def generate(cfg: dict, shot: dict, step: str, prompt: str, images: list, out_dir) -> tuple:
    """Render unless the hashed file exists. Returns (path, True if a call was made)."""
    path = out_dir / f"{shot['id']}_{key_hash(cfg, shot['seed'], prompt, images)}.jpg"
    if path.exists():
        return path, False
    image, entry = call_logged(lambda: render(cfg, prompt, shot["seed"], images),
                               stage="keyframes", model=cfg["model"], seed=shot["seed"],
                               params={"shot": shot["id"], "step": step, "steps": cfg["steps"],
                                       "size": f"{cfg['width']}x{cfg['height']}",
                                       "images": [str(p.relative_to(ROOT)) for p in images], "prompt": prompt})
    path.write_bytes(image)
    entry.update(output=str(path.relative_to(ROOT)), sha256=hashlib.sha256(image).hexdigest()[:16])
    log_call(**entry)
    return path, True


def run(only: set[str] | None) -> None:
    sb = load_storyboard()
    cfg = sb["models"]["keyframes"]
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    for shot in sb["shots"]:
        if only and shot["id"] not in only:
            continue
        scene, called = generate(cfg, shot, "scene", scene_prompt(sb, shot), [], SCENE_DIR)
        notes = ["scene " + ("generated" if called else "cached")]
        final, refs = scene, references(sb, shot)
        if refs and shot["size"] not in NO_IDENTITY_PASS:
            final, called = generate(cfg, shot, "identity", identity_prompt(shot, refs),
                                     [scene, *(p for _, p, _ in refs)], OUT_DIR)
            notes.append("identity " + ("generated" if called else "cached"))
        manifest[shot["id"]] = str(final.relative_to(ROOT))
        print(f"{shot['id']}  {final.relative_to(ROOT)}  ({', '.join(notes)})")
    order = [s["id"] for s in sb["shots"]]
    manifest = {k: manifest[k] for k in order if k in manifest}  # shot order, drops removed shots
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", help="comma-separated shot ids (default: all)")
    args = ap.parse_args()
    load_dotenv()
    missing = [k for k in ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN") if not os.environ.get(k)]
    if missing:
        raise SystemExit(f"Set {', '.join(missing)} in .env (see .env.example)")
    run(set(args.shots.split(",")) if args.shots else None)
