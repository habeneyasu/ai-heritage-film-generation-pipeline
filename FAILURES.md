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
