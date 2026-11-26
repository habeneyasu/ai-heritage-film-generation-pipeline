# One command: `make film` regenerates the film from storyboard.json.
# Every stage is cached by its inputs, so a re-run only redoes what changed. All generated
# model outputs are committed, so a fresh clone rebuilds the film with no API keys and no model calls
# (FFmpeg outputs such as the final MP4s are rebuilt, not committed).
# The GPU stages (Wan clips, music candidates) run on Kaggle: `make wan`, `make music`.

PY := uv run python -m
SHOTS ?= s02,s03,s04,s05,s06,s07,s08,s09,s10

.PHONY: film validate references keyframes narration shots score assemble radio-cut wan music status docker help

film: validate references keyframes narration shots score assemble  ## the whole film, 16:9 and 9:16

validate:            ## check storyboard.json against the schema and cross-field rules
	$(PY) pipeline.validate

references:          ## portrait options for characters without an approved reference
	$(PY) pipeline.references

keyframes: references  ## one image per shot (FLUX.2 klein, Cloudflare Workers AI)
	$(PY) pipeline.keyframes

narration:           ## one Tigrigna line per shot (Gemini TTS)
	$(PY) pipeline.narration

shots: keyframes     ## Wan clips where they exist, otherwise the storyboard's camera move
	$(PY) pipeline.shots

score:               ## join the chosen music candidates; skipped until cues are chosen (placeholder used)
	-$(PY) pipeline.music score

assemble:            ## edit, mix, subtitles, end card -> outputs/final/
	$(PY) pipeline.assemble

radio-cut:           ## narration and music on black, for user test 1
	$(PY) pipeline.assemble --radio-cut

wan:                 ## start Wan 2.2 clips on Kaggle (SHOTS=s09 for one); then `make status`, pull
	$(PY) pipeline.wan push --shots $(SHOTS)

music:               ## start ACE-Step candidates for every cue on Kaggle
	$(PY) pipeline.music push

status:              ## state of both Kaggle jobs
	-$(PY) pipeline.wan status
	-$(PY) pipeline.music status

docker:              ## build the image and run `make film` inside it
	docker build -t heritage-film .
	docker run --rm -v "$(CURDIR)/outputs:/app/outputs" $(if $(wildcard .env),--env-file .env,) heritage-film

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'
