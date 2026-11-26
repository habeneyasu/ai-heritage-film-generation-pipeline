# EXPERIMENTS.md

One entry per experiment. Change one thing at a time and keep the seed fixed when comparing.

## E01: Can Gemini TTS narrate in Tigrigna? (2026-11-25)
- **Hypothesis:** `gemini-3.8-flash-tts` pronounces Tigrigna, including the names ወልደቻኣል and ተስፋይ, well enough to narrate the film.
- **Change:** generated two call lines (ተስፋይ ሓወይ! / ወልደቻኣል ሓወይ!) and one opening sentence with both names, voice Sulafat, no style instruction. The sentence was then corrected by the author (ደጋ → ዶግዓ) and regenerated.
- **Result:** the author, a native Tigrigna speaker, judged the names and ሓወይ correctly pronounced and the speech natural. Audio: 1.4 s, 1.5 s and 8.3 s; latency 2.4–4.1 s per call (runs.jsonl, stage `narration-sample`). Re-running the script skipped the unchanged lines (input-hash cache).
- **Decision:** narrate in Tigrigna. The Amharic/English fallback is not needed. A second native-speaker check was planned but not done before submission (DESIGN.md section 7).

## E02: Does a style instruction improve the narration? (2026-11-25)
- **Hypothesis:** prefixing "Read in Tigrinya, slowly and warmly, like an elder telling a family story:" makes the voice warmer without changing the words.
- **Change:** the same opening sentence, same voice, with and without the English style prefix.
- **Result:** the styled version is about twice as long (15.2 s vs 8.3 s; first attempt 14.0 s vs 6.0 s). The author's listening verdict on warmth, and on whether the English instruction is spoken aloud, was not recorded.
- **Decision:** no style instruction (`"style": null` in storyboard.json). Doubling every line's length would push the film past 90 s: with plain narration it is already 89.5 s once each shot is lengthened to fit its line (E08). The author's listening verdict on warmth was not recorded, so this choice rests on timing, not on preference.

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

## E05: Does the Wan motion prompt need a camera move? (2026-11-25)
- **Hypothesis:** describing a "very slow push-in" (the storyboard's original camera language) gives a gentle, cinematic move in Wan 2.2.
- **Change:** s09 with "Very slow push-in; moonlight on their faces", then all nine people shots with prompts that keep the camera still and name only small movements ("Static camera, no zoom. The two brothers smile warmly at each other...").
- **Result:** the push-in was far from slow: by the last of 81 frames the faces filled the frame and the elder brother was half out of shot. With a static camera every clip kept its framing, and the movement went into the people instead: eating and pouring at the gathering, the greeting, one brother feeding the other ጉርሻ, the two heads leaning together in s09.
- **Decision:** static camera with named subject movement for every Wan shot; camera moves are kept only for the FFmpeg fallback, where they are exact.
- **Known deviation:** the prompt sent to Wan is the `motion_prompt` followed by the full `image_prompt` (`job_for` in `pipeline/wan.py`), so it re-describes the subject that the keyframe already shows. The brief's tips list this as a common mistake: for image-to-video, motion and camera are enough. In these nine clips it did no visible harm (identity, dress and framing held from the keyframe), and re-running every clip costs about three GPU hours, so the clips were kept. The next Wan run should send the motion prompt alone and be compared shot by shot.
- **Evidence:** runs.jsonl stage `shots`: s09 at 2026-11-25T19:10 (push-in) and the nine clips pulled at 2026-11-26T03:13 (static); `motion_prompt` in storyboard.json.

## E06: How do we get a real close-up? (2026-11-25)
- **Hypothesis:** writing "Tight close-up, heads and shoulders only" in the shot prompt is enough.
- **Change:** s09 with that wording and the full character descriptions, then with a face-only `close_up` description (face, hair, beard, gabi) used only in close-up shots; for the identity pass, full-length portraits versus a head-and-shoulders crop (`face_crop`).
- **Result:** with the full descriptions the scene was still full-length: trousers, sandals and the walking stick in the text pulled the camera back. The face-only text gave a true close-up. The identity pass with full-length portraits turned it back into two standing figures with distorted proportions; the face crop kept the close-up.
- **Decision:** close-ups use `close_up` text and `face_crop` references (s03, s09).

## E07: Wan clips or FFmpeg camera moves? (2026-11-25)
- **Hypothesis:** real motion from Wan 2.2 is worth its GPU time compared with a slow pan or zoom over the keyframe.
- **Change:** the same shots as camera moves (`pipeline/shots.py` fallback) and as Wan clips (704×704, 81 frames, 30 steps on Kaggle).
- **Result:** camera moves: all 11 shots in about 30 s on a laptop, no model call, but nobody moves. Wan: about 18 minutes per 3.4 s clip on a T4 (1061–1109 s for each of 9 clips, 2.8 GPU hours in one run), and people move naturally. The author found the draft with camera moves good but not yet natural (DESIGN.md section 8).
- **Decision:** Wan for the nine shots with people; camera moves for the two empty landscapes (s01, s11) and as the fallback for any failed clip.

## E08: Should narration set the length of the shots? (2026-11-25)
- **Hypothesis:** fixed shot lengths from the shot plan are fine if each line starts at its shot.
- **Change:** the first radio cut placed each line at its shot start and pushed it later when the previous line was still playing; assembly v1 lengthens a shot when its line plus a short pause does not fit.
- **Result:** with fixed lengths s01's line (6.9 s) ran past its 6 s shot and s02's line started 1.38 s late, so words and pictures drifted apart. With narration setting the cut, every line starts 0.4 s into its own shot; s01, s02 and s11 grew to 8.1 s, 12.1 s and 7.3 s, and the film to 89.5 s.
- **Decision:** narration sets the cut; the validator and assembly report the total against the 60–90 s limit.

## E09: How loud should the score sit under the voice? (2026-11-26)
- **Hypothesis:** the sidechain ducking alone keeps the score under the narration.
- **Change:** the chosen score mixed at its own level (−16.4 LUFS, about as loud as the voice), then 10 dB lower before ducking (`MUSIC_GAIN_DB`).
- **Result:** at its own level the score would compete with the narration between lines, because ducking only acts while the voice is present. At −10 dB, music-only passages measure −21.0 dB mean and narrated passages −15.6 to −17.4 dB, so the score comes up a little in the pauses and stays under the voice. The final mix is −14.3 LUFS integrated, −1.0 dBTP.
- **Decision:** a −10 dB music bed, then sidechain ducking and two-pass loudness normalisation.

## E10: Which music candidate for each cue? (2026-11-26)
- **Hypothesis:** three ACE-Step candidates per cue, with the same caption, tempo and key but different seeds, differ enough to be worth choosing between.
- **Change:** ACE-Step 1.5 turbo, 8 steps, instrumental, seeds 301–303, 311–313, 321–323; all nine generated in 6.5 minutes on one T4.
- **Result:** every candidate came back at the exact requested length. They differ clearly in level and dynamics (loudness range): gathering 2.1 / 1.1 / 2.9 LU, journey 5.8 / 7.2 / 13.3 LU, dawn 8.7 / 6.0 / 14.5 LU for candidates 1 / 2 / 3. The author listened and chose candidate 3 for every cue, which is also the most dynamic candidate in each.
- **Decision:** candidate 3 for gathering, journey and dawn (`chosen` in storyboard.json). The author chose by ear; no further reason was written down, so the measured difference above is the only recorded one.

## E11: Centre crop or per-shot crop for the two formats? (2026-11-25)
- **Hypothesis:** with subjects centred in every keyframe, a centre crop of the square shot works for both 16:9 and 9:16.
- **Change:** both crops drawn on all 11 keyframes, then a per-shot `crop` position in the storyboard where the subject was cut.
- **Result:** the centre crop cut heads in 16:9 (s02, s03, s04, s09, s10 have faces in the top third) and lost ተስፋይ completely from the 9:16 version of s02, the shot whose point is that he stands apart. Eight shots now carry a crop position. In 9:16, s04 and s09 cannot hold both brothers fully; the elder arriving (s04) and the centre of the two faces (s09) were chosen.
- **Decision:** square masters with a per-shot crop, checked on all 11 shots for both formats.

## E12: Should the edges of the Wan clips be trimmed? (2026-11-26)
- **Hypothesis:** as the brief's tips warn, many clips have a weak first or last half second, so trimming 0.25 s from each end before slowing them improves the shots.
- **Change:** looked at frames 0, 4, 72 and 80 of four clips (s04, s05, s07, s09) and measured the frame-to-frame change (FFmpeg `signalstats` YDIF) over the first and last four frames.
- **Result:** no weak edges. Frame 0 is the approved keyframe itself (image-to-video), and the first frames change smoothly (YDIF 2.8–5.9). The last frames show no flicker, morphing or collapse (YDIF 2.0–8.2) and carry each shot's meaning: the bite of ጉርሻ in s05, the brothers walking back in s07, the heads leaning together in s09. Trimming would also slow every clip further, because each 3.4 s clip is already stretched 1.5 to 2.7 times to fill its shot (5 to 9 s).
- **Decision:** no trimming. The edges are checked by eye whenever a clip is regenerated.
