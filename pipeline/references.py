"""Stage: character reference sheet (before keyframes).

    uv run python -m pipeline.references

Renders one portrait per seed in storyboard.json "reference_sheet" for each main character,
using the same character description and style block as the keyframes. The author picks one
option per character as the golden reference ("reference" in storyboard.json); keyframes are
then conditioned on it, and characters with an approved reference are skipped here.
Writes outputs/references/options/<character>_s<seed>_<hash>.jpg and a contact sheet per character.
"""

import hashlib
import subprocess

from dotenv import load_dotenv

from pipeline.common import ROOT, call_logged, log_call
from pipeline.keyframes import MAX_PROMPT, render
from pipeline.validate import load_storyboard

OUT_DIR = ROOT / "outputs" / "references" / "options"


def portrait_prompt(sb: dict, char_id: str) -> str:
    c = sb["characters"][char_id]
    prompt = f"{sb['reference_sheet']['prompt']} {c['role'][0].upper()}{c['role'][1:]}: {c['description']}. {sb['style_block']}"
    if len(prompt) > MAX_PROMPT:
        raise SystemExit(f"{char_id}: prompt is {len(prompt)} characters; the model accepts {MAX_PROMPT}")
    return prompt


def contact_sheet(paths: list, out) -> None:
    """Options side by side, labelled with their seed, for choosing the golden reference."""
    inputs, chains = [], []
    for i, p in enumerate(paths):
        inputs += ["-i", str(p)]
        seed = p.stem.split("_")[1]
        chains.append(f"[{i}]scale=384:512,drawtext=text='{seed}':x=10:y=10:fontsize=28:"
                      f"fontcolor=white:box=1:boxcolor=black@0.6[v{i}]")
    graph = ";".join(chains) + ";" + "".join(f"[v{i}]" for i in range(len(paths))) + f"hstack=inputs={len(paths)}"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
                    "-filter_complex", graph, "-frames:v", "1", str(out)], check=True)


def run() -> None:
    sb = load_storyboard()
    ref = sb["reference_sheet"]
    cfg = {**sb["models"]["keyframes"], "width": ref["width"], "height": ref["height"]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for char_id in ref["characters"]:
        if sb["characters"][char_id].get("reference"):
            print(f"{char_id}: approved reference {sb['characters'][char_id]['reference']} (skipped)")
            continue
        prompt = portrait_prompt(sb, char_id)
        paths = []
        for seed in ref["seeds"]:
            key = f"{cfg['model']}|{cfg['width']}x{cfg['height']}|{cfg['steps']}|{seed}|{prompt}"
            path = OUT_DIR / f"{char_id}_s{seed}_{hashlib.sha256(key.encode()).hexdigest()[:8]}.jpg"
            if not path.exists():
                image, entry = call_logged(lambda: render(cfg, prompt, seed), stage="references",
                                           model=cfg["model"], seed=seed,
                                           params={"character": char_id, "steps": cfg["steps"],
                                                   "size": f"{cfg['width']}x{cfg['height']}", "prompt": prompt})
                path.write_bytes(image)
                entry.update(output=str(path.relative_to(ROOT)), sha256=hashlib.sha256(image).hexdigest()[:16])
                log_call(**entry)
            paths.append(path)
        sheet = OUT_DIR.parent / f"{char_id}_options.jpg"
        contact_sheet(paths, sheet)
        print(f"{char_id}: {len(paths)} options -> {sheet.relative_to(ROOT)}")


if __name__ == "__main__":
    load_dotenv()
    run()
