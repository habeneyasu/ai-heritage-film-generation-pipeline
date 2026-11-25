# EXPERIMENTS.md

One entry per experiment. Change one thing at a time and keep the seed fixed when comparing.

## E01: Can Gemini TTS narrate in Tigrigna? (2026-11-25)
- **Hypothesis:** `gemini-3.8-flash-tts` pronounces Tigrigna, including the names ወልደቻኣል and ተስፋይ, well enough to narrate the film.
- **Change:** generated two call lines (ተስፋይ ሓወይ! / ወልደቻኣል ሓወይ!) and one opening sentence with both names, voice Sulafat, no style instruction. The sentence was then corrected by the author (ደጋ → ዶግዓ) and regenerated.
- **Result:** the author, a native Tigrigna speaker, judged the names and ሓወይ correctly pronounced and the speech natural. Audio: 1.4 s, 1.5 s and 8.3 s; latency 2.4–4.1 s per call (runs.jsonl, stage `narration-sample`). Re-running the script skipped the unchanged lines (input-hash cache).
- **Decision:** narrate in Tigrigna. The Amharic/English fallback is not needed. A second native speaker check is still pending (DESIGN.md section 7).

## E02: Does a style instruction improve the narration? (2026-11-25)
- **Hypothesis:** prefixing "Read in Tigrinya, slowly and warmly, like an elder telling a family story:" makes the voice warmer without changing the words.
- **Change:** the same opening sentence, same voice, with and without the English style prefix.
- **Result:** the styled version is about twice as long (15.2 s vs 8.3 s; first attempt 14.0 s vs 6.0 s). *Pending: the author's listening verdict, including whether the English instruction is spoken aloud.*
- **Decision:** *pending.*

## E03: Can the keyframes be reproduced from a seed? (2026-11-25)
- **Hypothesis:** the same prompt and seed give the same image, so keyframes can be regenerated exactly from storyboard.json.
- **Change:** on Cloudflare Workers AI, sent a `seed` to `flux-1-schnell`, then rendered one test prompt with `flux-2-klein-4b` at seed 101 twice and at seed 202 once (1024×1024, 4 steps).
- **Result:** `flux-1-schnell` rejects the field (`400: Additional or unevaluated properties '/seed' not allowed`). `flux-2-klein-4b` accepts it, but seed 101 gave two clearly different compositions (SSIM 0.69; seed 101 vs 202: 0.55), so the seed does not fix the image on this service. The test prompt also produced a European-looking thatched cottage with a chimney, a reminder that the full prompt (style block and shot detail) is needed to keep the look true to Tigray. These test calls were made by a throwaway script and are not in runs.jsonl.
- **Decision:** use `flux-2-klein-4b`. It accepts seed and size, and its reference-image editing may help keep the brothers consistent. Reproducibility comes from the input-hash cache: approved keyframes are committed, and a re-run reuses them instead of calling the model. Seeds are still sent and logged.

## E04: How should keyframes use the character references? (2026-11-25)
- **Hypothesis:** conditioning keyframes on one approved portrait per brother keeps them recognisably the same men in every shot.
- **Change:** three ways of making the same 11 keyframes, all with FLUX.2 klein 4B at 1024×1024, 4 steps:
  1. **Text only:** scene + full character description + style block.
  2. **Reference only:** the same prompt plus the approved portraits as input images.
  3. **Two-step:** the text-only scene first, then an edit call that keeps that image and makes each brother match his portrait. Close-ups get a head-and-shoulders crop of the portrait; the hands insert (s05) and the shots without people stay text only.
- **Result:**
  1. Text only: the younger brother changed age from shot to shot (mid-fifties, about 30, nearly a teenager), with cultural errors in early runs (FAILURES.md F04).
  2. Reference only: the brothers stayed consistent, but the model copied the portraits' setting and pose. The indoor gathering (s02–s04) moved outdoors in front of a house, s05 became a standing portrait with an inset picture, and no shot was a close-up.
  3. Two-step: the right scenes (indoor gathering, moonlit walks, dawn) with the brothers consistent where they are large in frame (s04, s06–s10, including the stick only for the elder). Limits: a small figure (ተስፋይ at the back of s02) barely changes, and close-up faces move only partly towards the portraits. Full-length portraits made close-ups full-length again; face crops fixed the framing.
- **Decision:** two-step, with face crops for close-ups. About 2 calls per shot with the brothers; every step is cached by its inputs, so a re-run makes no calls. Known issues kept for now: s01 does not show the homesteads clearly far apart, s11 has thatch on the main houses, close-up faces only partly match the portraits.
- **Evidence:** `docs/evidence/f04_keyframes_text_only.jpg` (1) and `docs/evidence/e04_keyframes_two_step.jpg` (3). Reference-only images were deleted after review; this entry describes them. runs.jsonl stage `keyframes` with `"step": "scene"` / `"identity"`.
