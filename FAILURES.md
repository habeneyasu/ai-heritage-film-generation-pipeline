# FAILURES.md

Real blockers (quota, memory, consistency, language): what broke, what was tried and what fixed it.

## F01: The Gemini TTS model is not listed and the default API version rejects it (2026-11-25)
- **What broke:** `models.list()` showed no TTS model. Calling `gemini-3.8-flash` with audio output failed with `400 INVALID_ARGUMENT: Unknown name "speechConfig" at 'generation_config'`.
- **What I tried:** the model names `gemini-3.8-flash`, `gemini-3.8-flash-tts`, `gemini-3.8-flash-preview-tts` and `gemini-2.5-flash-preview-tts`, on the SDK's default API version and on `v1beta` and `v1alpha`.
- **What fixed it:** `gemini-3.8-flash-tts` on the `v1beta` API (google-genai 3.6.1) returns `audio/wav`. Both are now constants in `pipeline/narration.py`.
- **Evidence:** the exploratory calls were made before logging existed, so they are not in runs.jsonl. The first logged calls show the working setup.

## F02: Free-tier rate limit after a few quick calls (2026-11-25)
- **What broke:** the fifth TTS call in about a minute returned `429 RESOURCE_EXHAUSTED` ("You exceeded your current quota").
- **What fixed it:** the retry in `pipeline/common.py` waited 2 s and the second attempt succeeded. Both attempts are logged.
- **Lesson:** keep TTS calls paced, and generate narration once per changed line (the input-hash cache) rather than re-running everything.
- **Evidence:** runs.jsonl, stage `narration-sample`, `"status": "error"`, attempt 1, followed by attempt 2 `"status": "ok"`.

## F03: TTS quota used up mid-run; retries wasted requests (2026-11-25)
- **What broke:** after re-running narration for 5 edited lines, s02 and s03 were generated, then s06 failed 4 times with `429 RESOURCE_EXHAUSTED`. Google's error said the free-tier limit is 10 requests per day for `gemini-3.8-flash-tts` and to retry in about 21 hours.
- **What did not add up:** runs.jsonl shows 20 successful TTS calls that same day, so the limit is not enforced as a strict 10 per day. When it actually resets is still to be confirmed by retrying later.
- **What fixed it:** `call_logged` in `pipeline/common.py` now reads the provider's suggested wait (`retryDelay`). If it is longer than 60 s, it stops at once (`QuotaExhausted`) instead of retrying. The narration stage then saves the lines done so far and exits with a clear message. Error text in runs.jsonl is no longer cut to 300 characters, so the quota details are kept.
- **Evidence:** runs.jsonl, stage `narration`, shot `s06`, attempts 1–4 with `"status": "error"`.

## F04: First keyframes drifted in identity and got the culture wrong (2026-11-25)
- **What broke:** the first text-only keyframes showed three men where there should be two, faces that read as Mediterranean, robes and aprons instead of the gabi, European bread rolls, light switches and a lattice window (`docs/evidence/f04_s04_first_attempt.jpg`). The first full set had the younger brother at three different ages, lanterns, bare feet and a village street instead of isolated homesteads (`docs/evidence/f04_keyframes_text_only.jpg`).
- **What I tried:**
  - Prompt wording from the author's cultural references: skin and face, the dress and footwear, houses entirely of stone with a thatched ኣጉዶ, moonlight instead of lanterns, the food on the መሶብ, and grandmothers preparing food and ጠላ. Photos the author shared were turned into text; none was sent to the model.
  - Four rounds of portrait options before the author approved two. The gabi came out as a towel (`docs/evidence/e04_portraits_first_gabi.jpg`), then as a neck scarf when the prompt said "wrapped high around the neck"; trousers were short and shirt and trousers differed in colour; the faces were too comfortable for the period ("weathered, sun-lined" fixed it).
  - Workers AI accepts at most 2048 characters per prompt. Detailed characters pushed the gathering shot over the limit several times; wording was tightened and the stage refuses to send a prompt that is too long.
- **What fixed it:** the author's approved portraits plus the two-step keyframes (EXPERIMENTS.md E04).

## F05: Wan 2.2 did not fit on a Kaggle T4 (2026-11-25)
- **What broke:** the model card asks for at least 24 GB of GPU memory; Kaggle's free GPUs are 2× Tesla T4 with about 14.5 GB each and no bfloat16.
  1. With Diffusers' model CPU offload in float16, the run failed with `CUDA out of memory` while moving a whole component to the GPU: the UMT5-XXL text encoder (~11 GB) and the 5B transformer (~10 GB) are each moved in one piece.
  2. With the text encoder on the second GPU and the transformer on the first (12.8 GB), generation started at about 16.5 s per step, then failed at step 3 with `cusolver error: CUSOLVER_STATUS_INTERNAL_ERROR`: the scheduler's tiny linear solve could not start a cuSOLVER handle on the nearly full GPU.
- **What fixed it:** encode every prompt on GPU 1 and then drop the text encoder; keep the transformer on GPU 0; solve the scheduler's small system on the CPU (same numbers); decode the video on GPU 1. The s09 clip then finished: 81 frames at 704×704 in 18.5 minutes, peak 14.9 GB on GPU 0.
- **Trade-off:** clips are 3.4 s, so `pipeline/shots.py` slows them to the shot length with motion interpolation; any shot without a clip uses its camera move.
- **Evidence:** runs.jsonl, stage `shots`, two `"status": "error"` lines (out of memory, cuSOLVER) followed by `"ok"` with `peak_gpu_gb` 14.94.
