# COSTS.md

What the film cost to make: model calls, time and money. The table comes straight from `runs.jsonl`
(`uv run python -m pipeline.costs`), so failed calls are counted too.

**Money spent so far: $0.** Every model ran on a free tier.

## Model calls (as of 2026-11-25 22:31 EAT)

| Stage | Model | Calls OK | Failed | Model time | Cost (USD) |
|---|---|---|---|---|---|
| keyframes | `@cf/black-forest-labs/flux-2-klein-4b` | 49 | 0 | 8.2 min | 0.00 |
| keyframes-seed-check | `@cf/black-forest-labs/flux-1-schnell` | 0 | 3 | 0.0 min | 0.00 |
| keyframes-test | `@cf/black-forest-labs/flux-2-klein-4b` | 4 | 0 | 0.7 min | 0.00 |
| narration | `gemini-3.8-flash-tts` | 14 | 9 | 1.3 min | 0.00 |
| narration-sample | `gemini-3.8-flash-tts` | 6 | 1 | 0.4 min | 0.00 |
| references | `@cf/black-forest-labs/flux-2-klein-4b` | 48 | 0 | 8.4 min | 0.00 |
| shots | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | 1 | 2 | 19.7 min | 0.00 |
| **Total** | | **122** | **15** | **38.7 min** | **0.00** |

Not in the table: about eight Cloudflare calls from throwaway test scripts (the seed and reference-field tests, EXPERIMENTS.md E03, E04), and the TTS calls made before logging existed (FAILURES.md F01).

## Free allowances used

| Service | What it ran | Allowance | Used |
|---|---|---|---|
| Google AI Studio (Gemini API) | Tigrigna narration | Free tier: about 10 TTS requests per day for this model, plus per-minute limits | Hit the daily limit twice (FAILURES.md F02, F03) |
| Cloudflare Workers AI | Reference portraits and keyframes | 10,000 neurons per day | Within the allowance; no call was refused |
| Kaggle notebooks (2× Tesla T4) | Wan 2.2 shots, ACE-Step music | 30 GPU hours per week | 0.9 h so far |

## Where the cost really is

- **Iteration, not the final images.** 82 of 101 logged image calls went on getting the look and the culture right: four rounds of portraits and three ways of making keyframes (EXPERIMENTS.md E04). The final keyframes need 19 calls (11 scenes and 8 identity edits).
- **GPU time for video.** One 3.4 s Wan clip takes about 18.5 minutes on a T4, because the model is split across two GPUs to fit in memory (FAILURES.md F05). Nine clips take about 3 GPU hours.
- **A re-run is free.** Every output is cached by its inputs and committed, so rebuilding the film from a fresh clone makes no model calls.
