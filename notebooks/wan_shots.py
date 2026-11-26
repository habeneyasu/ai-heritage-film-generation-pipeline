"""Kaggle GPU script: Wan 2.2 TI2V-5B image-to-video for the shots in jobs.json.

Pushed and run by `pipeline/wan.py`; do not run locally. Reads the attached dataset
(jobs.json + keyframes), writes one MP4 per job to /kaggle/working as soon as it is done
(sessions can time out), plus wan_log.jsonl with timing and GPU memory per clip.
"""

import glob
import json
import os
import subprocess
import sys
import time
import traceback

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "diffusers>=0.35", "ftfy"], check=True)

import torch  # noqa: E402
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline  # noqa: E402
from diffusers.utils import export_to_video, load_image  # noqa: E402

OUT = "/kaggle/working"
LOG = os.path.join(OUT, "wan_log.jsonl")


def log(**fields):
    with open(LOG, "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **fields}) + "\n")


jobs_path = glob.glob("/kaggle/input/**/jobs.json", recursive=True)[0]
data_dir = os.path.dirname(jobs_path)
spec = json.load(open(jobs_path))
log(event="start", gpu=torch.cuda.get_device_name(0), n_gpus=torch.cuda.device_count(),
    torch=torch.__version__, model=spec["model"])

# Two 16 GB T4s: the text encoder (~11 GB) and the transformer (~10 GB) do not fit on one GPU
# together (FAILURES.md F05). Encode every prompt on GPU 1 first, drop the encoder, then run the
# transformer and VAE on GPU 0 with the precomputed embeddings.
t0 = time.time()
vae = AutoencoderKLWan.from_pretrained(spec["model"], subfolder="vae", torch_dtype=torch.float32)
pipe = WanImageToVideoPipeline.from_pretrained(spec["model"], vae=vae, torch_dtype=torch.float16)
pipe.text_encoder.to("cuda:1")
embeds = {}
with torch.no_grad():
    for job in spec["jobs"]:
        pos, neg = pipe.encode_prompt(prompt=job["prompt"], negative_prompt=spec["negative_prompt"],
                                      do_classifier_free_guidance=True, device=torch.device("cuda:1"))
        embeds[job["shot"]] = (pos.to("cpu"), neg.to("cpu"))
pipe.text_encoder.to("cpu")
pipe.text_encoder = None
torch.cuda.empty_cache()
pipe.to("cuda:0")
pipe.vae.enable_tiling()

# The UniPC scheduler solves a tiny linear system every step; with GPU 0 nearly full, cuSOLVER
# cannot start (FAILURES.md F05). Solve it on the CPU instead: same numbers, no GPU memory.
_solve = torch.linalg.solve
torch.linalg.solve = lambda A, B, *a, **k: _solve(A.cpu().float(), B.cpu().float(), *a, **k).to(A.device, A.dtype)


def decode_on_gpu1(latents):
    """Decode on the second GPU, which is free after the text encoder is gone."""
    vae = pipe.vae.to("cuda:1")
    latents = latents.to("cuda:1", vae.dtype)
    mean = torch.tensor(vae.config.latents_mean).view(1, vae.config.z_dim, 1, 1, 1).to(latents)
    inv_std = 1.0 / torch.tensor(vae.config.latents_std).view(1, vae.config.z_dim, 1, 1, 1).to(latents)
    with torch.no_grad():
        video = vae.decode(latents / inv_std + mean, return_dict=False)[0]
    pipe.vae.to("cuda:0")
    return pipe.video_processor.postprocess_video(video, output_type="np")[0]
log(event="loaded", load_s=round(time.time() - t0, 1), gpu0_gb=round(torch.cuda.memory_allocated(0) / 1e9, 2))

for job in spec["jobs"]:
    out = os.path.join(OUT, job["output"])
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    try:
        image = load_image(os.path.join(data_dir, job["image"])).resize((job["width"], job["height"]))
        pos, neg = embeds[job["shot"]]
        frames = pipe(image=image, prompt_embeds=pos.to("cuda:0"), negative_prompt_embeds=neg.to("cuda:0"),
                      height=job["height"], width=job["width"], num_frames=job["frames"],
                      num_inference_steps=job["steps"], guidance_scale=job["guidance"],
                      generator=torch.Generator("cpu").manual_seed(job["seed"]), output_type="latent").frames
        frames = decode_on_gpu1(frames)
        export_to_video(frames, out, fps=job["fps"])
        log(event="clip", shot=job["shot"], output=job["output"], status="ok", latency_s=round(time.time() - t, 1),
            peak_gpu_gb=round(torch.cuda.max_memory_allocated() / 1e9, 2))
    except Exception as e:  # keep going: one failed shot falls back to a camera move
        log(event="clip", shot=job["shot"], output=job["output"], status="error", latency_s=round(time.time() - t, 1),
            error=f"{type(e).__name__}: {e}"[:1500], trace=traceback.format_exc()[-1500:])
log(event="done", total_s=round(time.time() - t0, 1))
