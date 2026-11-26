# Report: *A Love That Never Walked Alone*

Repository: https://github.com/habeneyasu/ai-heritage-film-generation-pipeline · Film: 16:9 and 9:16, 89.5 s, Tigrigna narration with English subtitles.

## 1. What I set out to make, and for whom

My father used to tell me about two brothers in a highland village in Tigray, ወልደቻኣል and ተስፋይ. Neither would celebrate at a gathering unless the other was there; each sent for his brother and waited. After a gathering, one walked the other home, then the other insisted on walking him back, and one night they walked back and forth until dawn, calling each other "ሓወይ" ("my brother"). I have lived away from home for about ten years, and my father is the last of his family who carries the story. I wanted to keep it.

**Audience:** anyone who watches, in any language, mostly on a phone. So the pictures had to carry the love on their own (actions, not words), the English subtitles had to be exact, and the narration had to stay in Tigrigna, because "ሓወይ" only works in Tigrigna. **Intent:** at the end, the viewer feels that love is something you do, and that the people who walk beside us are our true wealth. I wrote this in DESIGN.md before calling any model.

**Consent:** my father agreed to the story being told, and the brothers are shown as fictional interpretations, not likenesses (ETHICS.md). No real voice is cloned.

## 2. What I learned from my audience

**First test (the radio cut and an early draft).** Three people said "it's good" but answered none of my questions, so I recorded it as an assumption, not as evidence (DESIGN.md section 8). My own review as a native speaker was more useful: *it looks natural, but the storyboard needs more exact information.* The models filled every gap with a guess, and the guesses were wrong for Tigray: Mediterranean faces, European bread rolls, lanterns, bare feet, light switches, a village street instead of homesteads 10 km apart (FAILURES.md F04). So I made the storyboard exact: the dress described piece by piece from photos I shared, houses entirely of stone with a thatched ኣጉዶ, the night lit only by the moon, እንጀራ, ወጥ and ጠላ on the መሶብ, and grandmothers preparing the food.

**Second test (the near-final cut), two viewers.** This time the feedback was specific:
- the two brothers' skin and faces look closer to Arab than Ethiopian;
- the traditional dress does not come through as expected;
- the stone houses are good but need some refinement;
- overall it works, and what works best is the highland landscape and the narration.

**What I learned:** the landscape and the Tigrigna narration land; the people are the weak point. The reference portraits solved *consistency* (the same two men in every shot) but not *identity*: they are consistently the wrong kind of face, because the model's default face survives every prompt. That is a limit of the method, not of the prompt wording.

**What changed because of it:** I rewrote the characters from the viewers' three points: faces by skin, hair texture and face shape; shirt and trousers in different cloth, with each brother dressed differently; and inner walls plastered with earthen render while the outside stays stone (DESIGN.md section 9). The new storyboard is on its own branch, `feat/test2-storyboard`.

**What I could not do in time:** render it. The change touches every shot with the brothers, so it needs new portraits, all keyframes and three more GPU hours of Wan clips. The very first call was refused because Cloudflare's daily free allowance was used up (FAILURES.md F06). So the film I submit is the version the two viewers saw, and the change is ready to render with four commands when the allowance returns. I kept `main` consistent with the submitted film on purpose, so that `make film` from a clean clone still rebuilds exactly what I submitted.

## 3. The hardest problem, and how I solved it

**Keeping the two brothers the same men across eleven shots.** Text alone gave a younger brother who was 55 in one shot, 30 in the next and almost a teenager in a third (EXPERIMENTS.md E04). The suggested fix, a reference sheet, took four rounds before I approved two portraits: the gabi came out as a towel, then as a neck scarf, the trousers were short, the faces looked too comfortable for the period.

Using the portraits directly made things worse in a new way. The model copied the portrait's setting and pose, so the indoor gathering moved outdoors and the close-up became two standing men. What worked was splitting the job in two: make the scene from text first (setting, people, poses), then edit only the brothers to match their portraits, with a head-and-shoulders crop for close-ups (E04, E06). The result: the same two men in every shot where they are large enough to see.

A close second was making Wan 2.2 run at all on a free 16 GB GPU. It ran out of memory, then hit a cuSOLVER error, until I put the text encoder on the second GPU and moved one tiny calculation to the CPU (FAILURES.md F05). After that, all nine clips succeeded overnight.

## 4. Suggested practices, tested honestly

**A practice that beat my instinct: the reference sheet before keyframes.** My instinct was that a detailed enough prompt would keep the characters consistent. It did not: identity drifted across shots even with the same description word for word (E04, `docs/evidence/f04_keyframes_text_only.jpg`). Approved portraits used as references, in the two-step method, fixed it (`docs/evidence/e04_keyframes_two_step.jpg`). Without the suggestion I would have spent the time rewriting prompts.

**A practice that did not work as suggested: a fixed seed for reproducibility.** The brief says "the same seed with the same inputs gives the same result". On Cloudflare Workers AI, FLUX.1 schnell rejected the `seed` field outright, and FLUX.2 klein accepted it but gave two clearly different images for the same seed (SSIM 0.69; E03). So the seed could not make the film reproducible. What did: naming every output after a hash of its inputs and committing it, so a re-run reuses the exact files and a fresh clone rebuilds the film with no model calls.

## 5. Beyond the floor

- **Tigrigna, a language the brief could not confirm.** Gemini TTS narrated it well enough that I, a native speaker, judged the names and "ሓወይ" correctly pronounced (E01). Where it falls short: the free tier's daily limit stopped me twice (F02, F03), and a style instruction in English doubled the length of every line (E02). Image models cannot write Ge'ez, so all text is added in code.
- **Measured GPU work on free T4s:** 18 minutes per 3.4 s Wan clip, peak 14.9 GB, about $2.65 at list price for the whole film (COSTS.md), and a two-GPU split that others on Kaggle can reuse.

## 6. What I would build next

- A way for a relative who does not code to tell their own story and get a film back, using the same storyboard contract.
- A second native-speaker check of the narration, and Tigrigna subtitles alongside the English.
- Close-up faces that match the approved portraits more closely, for example a small LoRA trained on the portraits, measured against E04.

## Evidence index

DESIGN.md (audience, intent, user tests, change log) · EXPERIMENTS.md (E01–E11) · FAILURES.md (F01–F05) · COSTS.md (calls, latency, GPU minutes, list price) · ETHICS.md (consent, licences, labelling) · ARCHITECTURE.md · runs.jsonl
