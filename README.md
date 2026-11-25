# AI Heritage Film Generation Pipeline

A pipeline that turns one storyboard (`storyboard.json`) into a 60–90 second short film with keyframes, moving shots, an original score, narration and a finished edit, exported in 9:16 and 16:9.

The film tells a true family story from Tigray, narrated in Tigrinya with English subtitles.

> **Status:** project structure only. Setup and the one-command run (`make film`) will be documented here as each stage is implemented.

## Structure

```
storyboard.json   the contract between all stages
schema/           JSON Schema for the storyboard
pipeline/         one script per stage: script, keyframes, shots, music, narration, assemble
notebooks/        Kaggle notebooks for the GPU stages
outputs/          generated references, keyframes, shots, music, narration, edit, final
runs.jsonl        one log line per model call
Makefile          one command to run the whole pipeline
Dockerfile        reproducible environment
DESIGN.md · ARCHITECTURE.md · EXPERIMENTS.md · FAILURES.md · COSTS.md · ETHICS.md
```

## Licence

[MIT](LICENSE)
