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
