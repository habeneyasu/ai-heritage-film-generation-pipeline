# COSTS.md

What the film cost to make: model calls, time, GPU minutes and money. The table comes straight from `runs.jsonl` (`uv run python -m pipeline.costs`), so failed calls are counted too.

**Money spent: $0.** Every model ran on a free tier. **List-price equivalent: about $2.65**, almost all of it GPU time (see below).

## Model calls (final, 2026-11-26 11:15 EAT)

| Stage | Model | Calls OK | Failed | Model time | Cost (USD) |
|---|---|---|---|---|---|
| keyframes | `@cf/black-forest-labs/flux-2-klein-4b` | 49 | 0 | 8.2 min | 0.00 |
| keyframes-seed-check | `@cf/black-forest-labs/flux-1-schnell` | 0 | 3 | 0.0 min | 0.00 |
| keyframes-test | `@cf/black-forest-labs/flux-2-klein-4b` | 4 | 0 | 0.7 min | 0.00 |
| music | `ACE-Step 1.5` | 3 | 0 | 5.4 min | 0.00 |
| narration | `gemini-3.8-flash-tts` | 16 | 11 | 1.5 min | 0.00 |
| narration-sample | `gemini-3.8-flash-tts` | 6 | 1 | 0.4 min | 0.00 |
| references | `@cf/black-forest-labs/flux-2-klein-4b` | 48 | 3 | 8.4 min | 0.00 |
| shots | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | 10 | 2 | 182.0 min | 0.00 |
| **Total** | | **136** | **20** | **206.6 min** | **0.00** |

A music "call" is one cue with three candidates. Not in the table: about eight Cloudflare calls from throwaway test scripts (EXPERIMENTS.md E03, E04) and the TTS calls made before logging existed (FAILURES.md F01).

## Latency per call

| Stage | Typical latency | Notes |
|---|---|---|
| Narration (Gemini TTS) | 2.3–24 s per line, mean 5 s | Paced 4 s apart; one outlier of 24 s (s07, first run) |
| Images (FLUX.2 klein, Workers AI) | 5.6–16 s per image, mean 10 s | |
| Wan 2.2 clip (Kaggle 2× T4) | 1061–1109 s per 3.4 s clip | Plus about 5.5 min to load the model once per run |
| ACE-Step cue (Kaggle T4) | 81–157 s for three candidates | Plus about 1 min to set up the environment once per run |
| Assembly (FFmpeg, laptop) | about 90 s for both formats | No model calls |

## GPU minutes per stage (Kaggle, 2× Tesla T4)

| Stage | GPU session time | Of which generating | Notes |
|---|---|---|---|
| Moving shots (Wan 2.2) | about 205 min | 182 min | Three runs: out-of-memory test, cuSOLVER test, then 1 + 9 clips (FAILURES.md F05) |
| Music (ACE-Step 1.5) | about 7 min | 5.4 min | One run, nine candidates |
| **Total** | **3.55 h of the 30 h weekly quota** | | Kaggle's quota counter, 2026-11-26 |

## List-price equivalent

What the same work would cost at the providers' paid list prices:

| Item | Usage | List price | Equivalent |
|---|---|---|---|
| Gemini 3.8 Flash TTS | 113 s of audio = about 2,800 audio tokens (25 per second) | $9.00 per million audio output tokens (preview price until 31 Dec 2026) | $0.03 |
| FLUX.2 klein 4B on Workers AI | 101 images at 1024×1024 (4 tiles each) plus 48 input images | $0.000287 per output tile and $0.000059 per input tile ($0.011 per 1,000 neurons); four times this if metered per step (F06) | $0.13 (up to $0.51) |
| GPU time (Kaggle 2× T4) | 3.55 h × 2 GPUs | $0.35 per T4 per hour (Google Cloud on-demand, GPU only, VM not included) | $2.49 |
| **Total** | | | **about $2.65** (up to $3.05 if klein is metered per step) |

Sources: [Google Cloud Text-to-Speech pricing](https://cloud.google.com/text-to-speech/pricing), [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/), [Google Cloud GPU pricing](https://cloud.google.com/products/compute/gpus-pricing), checked on 2026-11-26. The per-image figure for klein is our arithmetic from Cloudflare's per-tile rate.

**Frontier comparison:** none. We had no access to the frontier lane (Omni Flash, Nano Banana, Lyria 3.5), so there is no frontier cost or quality to compare against.

## Free allowances

| Service | What it ran | Allowance | What we found |
|---|---|---|---|
| Google AI Studio (Gemini API) | Tigrigna narration | Free tier with per-minute and daily limits | The daily limit stopped us twice; the error said 10 requests per day, though 20 succeeded on the first day (FAILURES.md F02, F03) |
| Cloudflare Workers AI | Reference portraits and keyframes | 10,000 neurons per day | No call refused on the first day; on the second day the allowance was already used up before any call (FAILURES.md F06). If metered per step, an image costs about 416 neurons, not 105 |
| Kaggle notebooks (2× T4) | Wan 2.2, ACE-Step | 30 GPU hours per week; two sessions ran at the same time | 3.55 h used |

## Where the cost really is

- **Iteration, not the final images.** 82 of 101 logged image calls went on getting the look and the culture right: four rounds of portraits and three ways of making keyframes (EXPERIMENTS.md E04). The final keyframes need 19 calls.
- **GPU time for video.** One 3.4 s Wan clip takes about 18 minutes on a T4, because the model is split across two GPUs to fit in memory (FAILURES.md F05). That is 94% of the list-price equivalent.
- **A re-run is free.** Every model output is cached by its inputs and committed, so rebuilding the film from a fresh clone makes no model calls.
