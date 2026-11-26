# A Love That Never Walked Alone

**A heritage short film, and the reproducible multi-model pipeline that makes it from one storyboard.**

A true family story from Tigray: two brothers, ወልደቻኣል and ተስፋይ, who would not celebrate without each other, and who walked each other home, back and forth, until dawn. My father is the last of his family who carries this story; this film keeps it for the next generation.

> The characters are fictional AI-generated interpretations based on written family recollections. They are not verified historical likenesses.

## What it does

- Turns one validated `storyboard.json` into a finished film: 89.5 s, eleven shots, in 16:9 (1920×1080) and 9:16 (1080×1920).
- Keeps the two brothers consistent across shots with approved reference portraits (EXPERIMENTS.md E04).
- Narrates in Tigrigna, with burned-in English subtitles and a sidecar `.srt`.
- Adds an original score, ducked under the voice and normalised to −14 LUFS, and an end card saying the film was made with AI.
- Logs every model call to `runs.jsonl`, and regenerates only what a storyboard change affects.

## Models

| Stage | Model | Runs on |
|---|---|---|
| Character portraits and keyframes | FLUX.2 klein 4B | Cloudflare Workers AI (free tier) |
| Moving shots | Wan 2.2 TI2V-5B, image-to-video | Kaggle, 2× Tesla T4 (free GPU quota) |
| Narration | Gemini 3.8 Flash TTS (voice Sulafat) | Gemini API (free tier) |
| Music | ACE-Step 1.5 turbo, three candidates per cue | Kaggle, Tesla T4 |
| Edit, mix, subtitles, both formats | FFmpeg | locally |

The story and the narration were written with the author from family recollection, not generated.

## Run it

Requirements: [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 and the dependencies itself), FFmpeg with libass, the DejaVu Sans font (used for the subtitles), and `make`.

```bash
git clone https://github.com/habeneyasu/ai-heritage-film-generation-pipeline.git
cd ai-heritage-film-generation-pipeline
make film
```

The film is written to `outputs/final/heritage_16x9.mp4`, `outputs/final/heritage_9x16.mp4` and `outputs/final/heritage_en.srt`. From a clean clone this took 3 min 42 s, **with no API keys and no model calls**: every model output (portraits, keyframes, Wan clips, narration, music candidates) is committed and named after a hash of its inputs. Only what FFmpeg makes from them (stretched clips, score, mix, final MP4s) is rebuilt.

Keys are needed only to generate something new:

```bash
cp .env.example .env   # GEMINI_API_KEY, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, KAGGLE_API_TOKEN
```

## Change something

Edit `storyboard.json` (a prompt, a narration line, a shot length, a crop) and run `make film` again. Each stage skips what it already has, so a re-run with no changes prints `cached` throughout:

```
$ make narration
s01   6.88s speech / 6s shot  cached  LONGER THAN SHOT (assembly lengthens it)
s02  10.94s speech / 6s shot  cached  LONGER THAN SHOT (assembly lengthens it)
s03   2.67s speech / 6s shot  cached  OK
...
```

Change one narration line and only that line is generated again; the others stay `cached`, and `tail -1 runs.jsonl` shows the new call. A new keyframe has no Wan clip yet, so its shot uses the storyboard's slow zoom or pan until you run `make wan SHOTS=<id>` and pull the clip.

| Command | What it does |
|---|---|
| `make film` | Validate, references, keyframes, narration, shots, music score, assembly |
| `make radio-cut` | Narration and music on black with subtitles (user test 1) |
| `make wan SHOTS=s09` | Start Wan 2.2 clips on a Kaggle GPU; then `make status` and `uv run python -m pipeline.wan pull` |
| `make music` | Start ACE-Step music candidates on Kaggle; `pull`, set `chosen` per cue, then `make film` |
| `make help` | All targets, one per stage |

## Logging and cost

Each line of `runs.jsonl` is one model call: time, stage, model, parameters (including the prompt), seed, attempt, latency, cost, status and output file, plus the error when it failed, the image hash, the audio length or the peak GPU memory where they apply. Failed calls are kept: 136 calls succeeded and 20 failed.

**$0 spent**: every model ran on a free tier. At list prices the same work would cost **about $2.65**, almost all of it GPU time: 3.55 Kaggle GPU hours, mainly for nine Wan clips at about 18 minutes each. Details per stage: [COSTS.md](COSTS.md).

## Ethics

My father, the custodian of the story, gave permission for this film; the brothers are imagined, no photographs were used, and no real voice is cloned. The film ends with an AI end card, and the public post carries the platform's AI label. Consent, licences, provider terms and the review of generated outputs: [ETHICS.md](ETHICS.md).

## Limitations

- **User test 2** (two viewers) found the brothers' faces closer to Arab than Ethiopian, the dress too uniform, and the houses in need of plastered inner walls. The storyboard is updated on branch [`feat/test2-storyboard`](https://github.com/habeneyasu/ai-heritage-film-generation-pipeline/tree/feat/test2-storyboard) but not rendered: Cloudflare's daily free allowance ran out ([FAILURES.md](FAILURES.md) F06). `main` matches the submitted film, so `make film` rebuilds exactly what was submitted.
- Close-up faces match the approved portraits only partly, and the opening shot does not show clearly that the homes are about 10 km apart ([EXPERIMENTS.md](EXPERIMENTS.md) E04).
- The Tigrigna narration was checked by one native speaker, the author; a second listener was planned but not available in time.
- Free tiers set the pace: Gemini TTS allows about 10 requests a day, Workers AI 10,000 neurons a day, Kaggle 30 GPU hours a week.

## Documents

| | |
|---|---|
| [REPORT.md](REPORT.md) | The report: audience, what changed, hardest problem, practices tested, what next |
| [DESIGN.md](DESIGN.md) | Story, audience, characters and world, shot plan, user tests, change log |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Stages, the storyboard contract, caching, failure handling, the Kaggle GPU split |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Twelve experiments with hypotheses, results and decisions |
| [FAILURES.md](FAILURES.md) | Real blockers and how they were solved |
| [COSTS.md](COSTS.md) | Model calls, latency, GPU minutes and list price, from `runs.jsonl` |
| [ETHICS.md](ETHICS.md) | Consent, licences, AI disclosure |

## Structure

```
storyboard.json   the contract between all stages (validated by schema/storyboard.schema.json)
pipeline/         one module per stage: validate, references, keyframes, narration, shots (+ wan), music, assemble, costs
notebooks/        scripts that run on Kaggle GPUs (Wan 2.2, ACE-Step)
outputs/          references, keyframes, shots, narration, music, edit, final
docs/evidence/    before/after images cited in EXPERIMENTS.md and FAILURES.md
runs.jsonl        one log line per model call
Makefile          one command to run the pipeline
.env.example      the keys and optional settings, names only
```

## Acknowledgements

Made for the 10 Academy TRP AI content generation challenge.

## Licence

Code: [MIT](LICENSE). Model licences and provider terms: [ETHICS.md](ETHICS.md).

---

**Made with AI, guided by family memory.**
