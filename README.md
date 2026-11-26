# AI Heritage Film Generation Pipeline

A pipeline that turns one storyboard (`storyboard.json`) into a 60–90 second short film with keyframes, moving shots, an original score, narration and a finished edit, exported in 16:9 and 9:16.

The film, *A Love That Never Walked Alone*, tells a true family story from Tigray: two brothers who would not celebrate without each other, and who walked each other home, back and forth, until dawn. It is narrated in Tigrigna with English subtitles.

> The characters are fictional AI-generated interpretations based on written family recollections. They are not verified historical likenesses.

## Run it

Requirements: [uv](https://docs.astral.sh/uv/), FFmpeg (with libass), `make`. Or use Docker (`make docker`).

```bash
git clone https://github.com/habeneyasu/ai-heritage-film-generation-pipeline.git
cd ai-heritage-film-generation-pipeline
make film
```

The film is written to `outputs/final/heritage_16x9.mp4`, `outputs/final/heritage_9x16.mp4` and `outputs/final/heritage_en.srt`.

Every model output (images, Wan clips, narration, music candidates) is committed and named after a hash of its inputs, so a fresh clone rebuilds the film **with no API keys and no model calls**. What FFmpeg makes from them (stretched clips, score, mix, final MP4s) is rebuilt in a few minutes rather than committed. Keys are only needed when you change the storyboard:

```bash
cp .env.example .env   # GEMINI_API_KEY, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, KAGGLE_API_TOKEN
```

## Change something

Edit `storyboard.json` (a prompt, a narration line, a shot length, a crop) and run `make film` again. Only what depends on the change is regenerated; everything else prints `cached`.

| Command | What it does |
|---|---|
| `make film` | Validate, references, keyframes, narration, shots, music score, assembly |
| `make radio-cut` | Narration and music on black with subtitles (user test 1) |
| `make wan SHOTS=s09` | Start Wan 2.2 clips on a Kaggle GPU; then `make status` and `uv run python -m pipeline.wan pull` |
| `make music` | Start ACE-Step music candidates on Kaggle; `pull`, set `chosen` per cue, then `make film` |
| `make help` | All targets |

## Documents

| | |
|---|---|
| [DESIGN.md](DESIGN.md) | Story, audience, characters and world, shot plan, user tests, change log |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Stages, the storyboard contract, caching, the Kaggle GPU split |
| [EXPERIMENTS.md](EXPERIMENTS.md) | What was tried, with results and decisions |
| [FAILURES.md](FAILURES.md) | Real blockers and how they were solved |
| [COSTS.md](COSTS.md) | Model calls, time and money, from `runs.jsonl` |
| [ETHICS.md](ETHICS.md) | Consent, licences, AI disclosure |

## Structure

```
storyboard.json   the contract between all stages (validated by schema/storyboard.schema.json)
pipeline/         one module per stage: references, keyframes, shots (+ wan), narration, music, assemble
notebooks/        scripts that run on Kaggle GPUs (Wan 2.2, ACE-Step)
outputs/          references, keyframes, shots, narration, music, edit, final
docs/evidence/    before/after images cited in EXPERIMENTS.md and FAILURES.md
runs.jsonl        one log line per model call
Makefile          one command to run the pipeline
Dockerfile        reproducible environment for the local stages
```

## Licence

Code: [MIT](LICENSE). Model licences and provider terms: [ETHICS.md](ETHICS.md).
