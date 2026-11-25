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
