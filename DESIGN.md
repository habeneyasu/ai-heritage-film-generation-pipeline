# DESIGN.md — "A Love That Never Walked Alone"

> Brief written on 2026-11-25, **before any model was called or any asset generated**.

## 1. The story

A true story passed down in my family, told to me by my father when I was a child. Two brothers, **ወልደቻኣል** (the elder) and **ተስፋይ**, were respected and well established in their community. Their love for each other was shown in what they did:

- **Neither was happy at a gathering unless the other was there.** When there was a gathering, whether an official occasion or a simple family one, neither would sit down and take part alone. He would ask the people around him, *"ወልደቻኣል ሓወይ ፀውዕዎ"* / *"ተስፋይ ሓወይ ፀውዕዎ"* ("call my brother"), and wait until his brother arrived. Only then would he join the gathering.
- **Neither would let the other walk home alone.** Their homes were approximately 10 km apart (based on family recollection). After a gathering, one walked the other home, and then the other insisted on walking him back. They took turns accompanying each other, and on one night they walked back and forth until the night turned into dawn.
- They called each other **"ተስፋይ ሓወይ!" / "ወልደቻኣል ሓወይ!"** ("my brother").

**Why it matters to me:** my father is the last of his family who carries this story. The film keeps it alive for the next generation.

**Logline:** Two brothers in a highland village love each other so much that neither will celebrate at a gathering without the other and neither will let the other walk home alone, so they walk each other back and forth until dawn.

## 2. Audience

**Anyone who watches the film**, whatever their language or background, should be able to follow and feel the story. Most will watch on a phone (vertical, 9:16), and some on YouTube or a larger screen (horizontal, 16:9).

What this means for the design:
- **The pictures must carry the story on their own.** The love is shown in actions (waiting for his brother before celebrating, walking each other home), so the film still works for someone who reads no subtitles.
- **The English subtitles must be accurate and easy to read**, because most viewers will not speak Tigrigna.
- **Both groups are tested:** Tigrigna speakers check the narration and the names, and non-Tigrigna speakers check that the story is clear through the pictures and subtitles alone.

## 3. Intent

The film shows true love through action rather than words: refusing to celebrate without your brother, and refusing to let him walk alone. The narration tells the story, but the pictures carry the love.

**The central message is brotherly love and loyalty.** The brothers' wealth and standing in the community are background details only. They are not shown as a theme and not emphasised in the narration.

**At the end, the viewer should feel that love is something you do, and that the people who walk beside us are our true wealth.** Ideally they think of someone they would walk home.

**Define statement:** *How might we help anyone, in any language, feel the love between two brothers from three generations ago, and recognise it in their own lives?*

## 4. Constraints and decisions

| Decision | Choice | Reason |
|---|---|---|
| Length | About 80 s planned; **89.5 s in the cut** (60–90 s required) | Enough for one complete story with a clear ending. The cut is longer because each shot now lasts at least as long as its narration line (s01, s02 and s11 grew; EXPERIMENTS.md E08) |
| Pacing | More than half the running time (about 42 s) goes to the repeated journey (shots 6–10) | The journey is the emotional heart; the gathering sets it up quickly |
| Narration language | **Tigrigna** | It is the brothers' language; the call ሓወይ only works in Tigrigna. If Gemini TTS handles Tigrigna badly, the fallback is Amharic or English narration with the ሓወይ lines kept in Tigrigna, and the failure goes in FAILURES.md. |
| Narration framing | A generic, passed-down voice ("in a highland village in Tigray, there lived two brothers, ወልደቻኣል and ተስፋይ…"), not as a named family relation. The names are kept; the last line says it is a story I grew up hearing. | The film reaches anyone as a timeless story and reveals fewer family details. The family relation is recorded only in ETHICS.md, for consent. |
| Narrator voice | Gemini TTS voice, not a cloned voice | No real person's voice is replicated (see ETHICS.md) |
| Subtitles | English, burned in, one sentence per subtitle and at most 2 lines; a longer line is split into two timed subtitles in code (EXPERIMENTS.md E13) | Makes the film understandable to anyone; kept inside the 9:16 safe area |
| Text in images | None; all titles and text are added in code | Image models garble the Ge'ez script |
| Region | Kept vague ("a highland village in Tigray") | Privacy |
| Era | Approximately mid-20th century | Based on family recollection |
| Distance between homes | Approximately 10 km | Based on family recollection |
| Politics | Left out | The film is about the brothers |

## 5. Characters and world (continuity bible)

Both brothers wear the same traditional rural dress, so other features tell them apart in every shot:

| | ወልደቻኣል | ተስፋይ |
|---|---|---|
| Age (estimate) | Late fifties; slightly the elder | Late fifties |
| Face and skin | Deep brown skin; lean, with a slender, weathered, sun-lined face and work-worn hands (life was harder then) | Same |
| Beard and hair | Short, tightly curled grey hair; grey beard | Short, tightly curled dark greying hair; dark beard turning grey |
| In hand | One rough wooden walking stick with a curved crook handle, held in one hand | — |
| Clothing | Shirt and trousers of the same off-white handwoven cotton: long-sleeved shirt to the knees, full-length trousers to the ankles, loose at the hips and narrow at the ankles; a broad, blanket-like white cotton gabi with a crinkled, layered texture, covering both shoulders and upper arms, its top edge folded loosely around the neck; no head covering | Same |
| Footwear | Dark grey closed-toe sandals with cut-out openings and a buckled ankle strap; never barefoot, no modern shoes | Same |

*Ages are estimates. Family recollection gives only that the brothers were about the same age and ወልደቻኣል was slightly older (roughly 3 years).*

**Grandmothers** (at the gathering): ordinary rural women with weathered faces and work-worn hands, not ceremonial costume. A long white cotton ቀሚሽ to the ankles with long sleeves, a dark woven ጥበብ band running down the front in a V from the neckline and small embroidered crosses on the chest, a white ነጠላ over the shoulders or head, ሹሩባ braided tight on top and fuller at the back and sides, small round earrings, a thin neck cord and practical footwear. They prepare the food and ጠላ.

**Homes:** each brother has the same kind of homestead, and they live the same way of life. The homesteads are approximately **10 km apart** (based on family recollection), and they differ only slightly in size. Each one has:
- **ህድሞ**: a round house built entirely of stone.
- **ሳፁን**: a rectangular (four-sided) house built entirely of stone.
- **ኣጉዶ**: a separate kitchen hut with a grass-thatched roof.

*Continuity: the two homesteads are drawn from one shared description, so they look almost the same. That is deliberate. The distance between them is what separates the brothers, and arriving at near-identical doors again and again strengthens the back-and-forth motif. The passing night (dusk, moon, then dawn) shows the progress, not the houses.*

**Place:** the Tigray highlands, with a rocky mountain ridge behind, stone terraces, and dry-stone field walls.

**Gathering objects and food:** one large round እንጀራ covering the መሶብ with small mounds of different ወጥ (meat, red lentil, yellow split peas, greens) and rolled እንጀራ around the edge, ሕምባሻ, milk, honey (መዓር), ኣጅቦ, ጠስሚ and ጠላ, served on a መሶብ, with a ጀበና. The brothers carry no lamp or lantern; at night the only light is the moon.

*The author checked the cultural terms on 2026-11-25: ዓይቢ was corrected to ኣጅቦ, and ጥሕሎ was removed.*

### Visual consistency rules (applied to every image and video prompt)

1. **Style:** cinematic historical realism with natural light, warm earth tones and soft film grain. No cartoon, fantasy or painterly-illustration look.
2. **Landscape and architecture:** authentic Tigray highlands (rocky ridges, stone terraces, dry-stone walls, sparse trees) and the homestead buildings described above. Nothing invented or from another region.
3. **Characters:** the same two descriptions from the table above, word for word, in every prompt. Generated against one approved character reference sheet.
4. **Clothing:** traditional rural Tigrayan dress as described above, in every shot; footwear always, never barefoot. No mixing of dress or architecture from other Ethiopian regions.
5. **Period:** mid-20th century. **No modern elements**: no plastic, metal roofs, power lines, vehicles, phones, modern clothing or printed text.
6. **Night light:** moonlight only; no lamps or lanterns. The sky moves steadily from dusk, through deep night, to dawn across the shots.

## 6. Shot plan (v2, before user test 1)

| # | Shot | Size | Reason it exists | ~s |
|---|---|---|---|---|
| 1 | Two similar homesteads (ህድሞ, ሳፁን, ኣጉዶ) far apart across the valley, mountain behind, dusk | Extreme wide | Place, and the distance between the brothers | 6 |
| 2 | A gathering: እንጀራ, ወጥ and ጠላ on the መሶብ, grandmothers preparing food and ጠላ, people sit down, but ተስፋይ stays standing and does not celebrate | Medium | Love in action #1: he will not take part without his brother | 6 |
| 3 | ተስፋይ asks the people around him: "ወልደቻኣል ሓወይ ፀውዕዎ"; someone sets off to call him | Close-up | The request: he sends for his brother and waits | 6 |
| 4 | ወልደቻኣል arrives with his stick; only then does ተስፋይ sit beside him and join the celebration | Wide | The wait ends; they are always together | 6 |
| 5 | Hands: one brother gives the other a gursha | Close-up insert | Love without words | 5 |
| 6 | Dusk into night: they leave together; ወልደቻኣል walks ተስፋይ home | Wide | The journey begins | 7 |
| 7 | At ተስፋይ's homestead: he will not let his brother go alone and turns back to walk him home | Medium | The loop begins: they take turns | 8 |
| 8 | At ወልደቻኣል's homestead, the moon high: now ወልደቻኣል turns back to walk ተስፋይ home | Medium | The loop repeats; the night deepens | 9 |
| 9 | Faces in moonlight on the path: "ተስፋይ ሓወይ!" / "ወልደቻኣል ሓወይ!" | Close-up | The heart of the film | 9 |
| 10 | The sky pales from night to dawn; they still walk side by side | Wide | Night turns into dawn; they never said goodbye | 9 |
| 11 | The empty path in full daylight | Extreme wide | The story lives on in those who heard it | 6 |
| 12 | AI end card (added in code) | — | Required disclosure | 3 |

**Total: about 80 s.** The repeated journey (shots 6–10) gets about 42 s, more than half the film.

Subjects are composed in the centre of the frame so that the 9:16 and 16:9 versions can be cut from the same material.

## 7. Early check: Tigrigna narration sample

**Status:** run on 2026-11-25 with `gemini-3.8-flash-tts`, voice Sulafat (`uv run python -m pipeline.narration --sample`; see EXPERIMENTS.md E01). **Result: narrate in Tigrigna.**

1. Generate a short sample with Gemini TTS: the two ሓወይ lines and one or two narration sentences that include both names.
2. A native Tigrigna speaker listens and checks:
   - the pronunciation of ወልደቻኣል, ተስፋይ and ሓወይ,
   - whether the speech sounds natural (rhythm, stress, tone),
   - whether the English subtitles match the meaning.
3. The result goes in EXPERIMENTS.md, and in FAILURES.md if the TTS falls short. It decides whether to narrate in Tigrigna or use the fallback (see section 4).

| Listener (role, not name) | Pronunciation | Naturalness | Subtitle accuracy | Decision |
|---|---|---|---|---|
| Author (native Tigrigna speaker) | ወልደቻኣል, ተስፋይ and ሓወይ correct | Natural | "ኣብ ሓንቲ ዓዲ ዶግዓ ትግራይ…" = "In a highland village in Tigray…" matches | Narrate in Tigrigna |
| Second native speaker | Not done before submission | | | Planned; no second listener was available in time |

## 8. User test 1: radio cut (narration over placeholder music, black screen)

**Status:** run informally on 2026-11-25; **no structured answers were collected.** The result below is recorded as an assumption, not as audience evidence.

**Plan:** at least 3 people, in person or on Slack, including at least one Tigrigna speaker (to check the narration and names) and at least one non-Tigrigna speaker (to check the story through the subtitles alone). Questions:
1. In one sentence, what was the story about?
2. What did you feel at the end?
3. Which moment stayed with you?
4. Was anything confusing, too fast or too long?
5. Were the Tigrigna words and the names ወልደቻኣል and ተስፋይ pronounced correctly?

| Person (role, not name) | What they said | Insight |
|---|---|---|
| Viewer 1 | "It's good" (no answers to the questions) | Not enough to learn from |
| Viewer 2 | "It's good" (no answers to the questions) | Not enough to learn from |
| Viewer 3 | "It's good" (no answers to the questions) | Not enough to learn from |
| The author (native Tigrigna speaker) | It looks natural, but the storyboard needs more exact information | The main finding of this round |

**Assumption:** the story and narration work well enough to continue. It rests on three short "it's good" replies and the author's own review, not on answers to the questions above. User test 2 uses a written questionnaire so that the answers can be recorded.

**General feedback:** the film feels natural; what it needs is more exact information in the storyboard, so that what is generated matches how life really was, rather than the model's guess.

**What changed because of it:** the storyboard was made more exact throughout, from the author's cultural references:
- Characters: about the same age, deep brown skin, weathered faces, dress described piece by piece (shirt, trousers, gabi, sandals), one walking stick for the elder only.
- World: houses entirely of stone with a thatched ኣጉዶ, homesteads far apart, moonlight only (no lanterns), the food on the መሶብ, grandmothers preparing food and ጠላ.
- Motion: every Wan `motion_prompt` states exactly what moves and keeps the camera still, instead of a general camera move.
- Framing: a per-shot `crop` keeps the subject in both the 16:9 and 9:16 versions.
- Music: three ACE-Step candidates per cue replace the placeholder, chosen by listening.

## 9. User test 2: near-final cut

**Status:** run on 2026-11-26 with the near-final cut (Wan clips, chosen score), with **two viewers**. Feedback collected and relayed by the author; their roles were not recorded.

| What they said | Insight | Change |
|---|---|---|
| The two brothers' skin and faces look closer to Arab than Ethiopian | The references fixed consistency, not identity: the model's default face survives (EXPERIMENTS.md E04) | Faces described by skin, hair texture and face shape: dark brown skin, short tightly coiled hair, a long narrow face with high cheekbones (ወልደቻኣል) and an oval face (ተስፋይ) |
| The traditional dress does not come through as expected: shirt and trousers look like one uniform, and both brothers are dressed the same | Matching cloth for shirt and trousers, and identical outfits, read as a costume | Shirt and trousers now differ, and the brothers dress differently: ወልደቻኣል in an off-white knee-length shirt, khaki-brown trousers and a broad gabi; ተስፋይ in a light grey shirt, dark brown trousers and a lighter gabi |
| The stone houses are good, but need refinement | Outside stone is right; inside, the walls were bare stone | Inner walls plastered smooth with earthen render; outer walls stay stacked stone |
| Overall good; the highland landscape and the narration work best | The setting and the Tigrigna narration land; the people are the weak point | Landscape shots and narration unchanged |

**What changed because of it:** the storyboard was updated for all three points (branch `feat/test2-storyboard`, commit `091df8a`). The approved portraits were cleared, because the faces and dress they carry are the ones the viewers criticised, so new portraits must be chosen first.

**Not yet in the submitted film.** Rendering the change needs new portraits, all keyframes and new Wan clips. The first call was refused: Cloudflare's daily free allowance was already used up (FAILURES.md F06). The submitted film is therefore the version the viewers saw; the change is ready to render with `make references`, `make keyframes`, `make wan` and `make film` once the allowance returns.

## 10. Storyboard change log

| Date | Change | Caused by |
|---|---|---|
| 2026-11-25 | Shot 3: "settling the bill" removed; it was a family gathering | The author's correction of the first draft |
| 2026-11-25 | Added the "won't join a gathering alone, call my brother" beat (shots 2–3) | The author's account of the gatherings |
| 2026-11-25 | Reframed from drinking to gathering; tela removed | The author: drinking could give the wrong meaning |
| 2026-11-25 | Father's age removed | The author's privacy preference |
| 2026-11-25 | Homes specified as ህድሞ (round), ሳፁን (rectangular) and ኣጉዶ (grass-roofed kitchen hut) | The author's description |
| 2026-11-25 | Both brothers have the same kind of homestead and way of life; only the 10 km distance (and a slight difference in size) separates them | The author's correction |
| 2026-11-25 | Both brothers in white gabi; told apart by age, beard and walking stick | The author's description |
| 2026-11-25 | Audience widened from "Tigrigna-speaking families" to anyone who watches; the pictures and subtitles must carry the story | The author's decision |
| 2026-11-25 | ጥሕሎ removed from the gathering foods | The author's correction |
| 2026-11-25 | Family relation and "Tigrayans" removed from the story text; the narration is told as a passed-down story | The author's privacy preference |
| 2026-11-25 | Era and distance stated as approximate, based on family recollection | The author's review |
| 2026-11-25 | Gathering beat strengthened: he asks people to call his brother and waits until he arrives (shots 2–4) | The author's review |
| 2026-11-25 | Journey shows the brothers taking turns at each homestead, with night turning into dawn (shots 6–10) | The author's review |
| 2026-11-25 | Timing rebalanced within about 80 s: the journey now gets about 42 s | The author's review |
| 2026-11-25 | Visual consistency rules added; Tigrigna sample check added before the radio cut | The author's review |
| 2026-11-25 | Wealth and status made background only; brotherly love and loyalty are the central message | The author's review |
| 2026-11-25 | Opening sentence: ደጋ replaced with ዶግዓ | The author's correction during the Tigrigna sample check |
| 2026-11-25 | Wording aligned with storyboard.json: "celebrate" at gatherings; closing line "a story I grew up hearing"; brothers about 3 years apart | The author's review of the narration |
| 2026-11-25 | s02 line: neither was happy at a gathering without the other, and each sent for his brother; s03 now only the waiting | The author's rewrite of the Tigrigna line |
| 2026-11-25 | Brothers about the same age; dress, footwear and grandmothers specified; houses entirely stone with a thatched ኣጉዶ; no lanterns (moonlight only); እንጀራ, ወጥ and ጠላ added, with grandmothers preparing food and ጠላ | The author's cultural references, after the first keyframes |
| 2026-11-25 | Wan motion prompts rewritten as static camera with small natural movement; Wan clips replace camera moves for s02–s10; placeholder drone to be replaced by an ACE-Step score | User test 1 (general feedback: natural, but the storyboard needs more exact information) |
| 2026-11-26 | Narration sets the cut: a shot lasts at least as long as its line (s01 8.1 s, s02 12.1 s, s11 7.3 s; total 89.5 s); per-shot crop for 16:9 and 9:16; ACE-Step candidate 3 chosen for each cue | Radio cut timing (s02 started 1.4 s late), the crop check on all 11 shots, and the author's listening |
| 2026-11-26 | Faces (skin, hair texture, face shape), distinct dress per brother with shirt and trousers that differ, inner walls plastered with earthen render; approved portraits cleared (branch `feat/test2-storyboard`, not rendered yet) | User test 2 (two viewers) |
| 2026-11-26 | Subtitles: one sentence per subtitle and at most 60 characters, split in code; s01, s02, s07, s08, s09 and s11 now show as two subtitles each | Final check of the 9:16 cut: three subtitles wrapped to three lines (EXPERIMENTS.md E13) |
