# DESIGN.md — "A Love That Never Walked Alone"

> Brief written on 2026-11-25, **before any model was called or any asset generated**.

## 1. The story

A true story passed down in my family, told to me by my father when I was a child. Two brothers, **ወልደቻኣል** (the elder) and **ተስፋይ**, were respected and well established in their community. Their love for each other was shown in what they did:

- **Neither would celebrate at a gathering without the other.** When there was a gathering, whether an official occasion or a simple family one, neither would sit down and take part alone. He would ask the people around him, *"ወልደቻኣል ሓወይ ፀውዕዎ"* / *"ተስፋይ ሓወይ ፀውዕዎ"* ("call my brother"), and wait until his brother arrived. Only then would he join the gathering.
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
| Length | About 80 s (60–90 s required) | Enough for one complete story with a clear ending |
| Pacing | More than half the running time (about 42 s) goes to the repeated journey (shots 6–10) | The journey is the emotional heart; the gathering sets it up quickly |
| Narration language | **Tigrigna** | It is the brothers' language; the call ሓወይ only works in Tigrigna. If Gemini TTS handles Tigrigna badly, the fallback is Amharic or English narration with the ሓወይ lines kept in Tigrigna, and the failure goes in FAILURES.md. |
| Narration framing | A generic, passed-down voice ("in a highland village in Tigray, there lived two brothers, ወልደቻኣል and ተስፋይ…"), not as a named family relation. The names are kept; the last line says it is a story I grew up hearing. | The film reaches anyone as a timeless story and reveals fewer family details. The family relation is recorded only in ETHICS.md, for consent. |
| Narrator voice | Gemini TTS voice, not a cloned voice | No real person's voice is replicated (see ETHICS.md) |
| Subtitles | English, burned in, at most 2 lines and about 40 characters | Makes the film understandable to anyone; kept inside the 9:16 safe area |
| Text in images | None; all titles and text are added in code | Image models garble the Ge'ez script |
| Region | Kept vague ("a highland village in Tigray") | Privacy |
| Era | Approximately mid-20th century | Based on family recollection |
| Distance between homes | Approximately 10 km | Based on family recollection |
| Politics | Left out | The film is about the brothers |

## 5. Characters and world (continuity bible)

Both brothers wear a **white gabi**, so other features tell them apart in every shot:

| | ወልደቻኣል | ተስፋይ |
|---|---|---|
| Age (estimate) | Late fifties; the elder, by about 3 years | Mid-fifties |
| Beard and hair | Grey beard, grey hair | Dark beard just beginning to grey |
| In hand | Walking stick | — |
| Clothing | White gabi | White gabi |

*Ages are estimates. Family recollection gives only that ወልደቻኣል was the elder, by roughly 3 years. The ages in the prompts are chosen to give both men a believable look.*

**Homes:** each brother has the same kind of homestead, and they live the same way of life. The homesteads are approximately **10 km apart** (based on family recollection), and they differ only slightly in size. Each one has:
- **ህድሞ**: a round house built of stone.
- **ሳፁን**: a rectangular (four-sided) stone house.
- **ኣጉዶ**: a kitchen hut roofed with grass.

*Continuity: the two homesteads are drawn from one shared description, so they look almost the same. That is deliberate. The distance between them is what separates the brothers, and arriving at near-identical doors again and again strengthens the back-and-forth motif. The passing night (moon, lantern, then dawn) shows the progress, not the houses.*

**Place:** the Tigray highlands, with a rocky mountain ridge behind, stone terraces, and dry-stone field walls.

**Gathering objects and food:** ሕምባሻ, milk, honey (መዓር), ኣጅቦ, ጠስሚ, a መሶብ, a ጀበና. At night the light comes from a kerosene lantern and the moon.

*The author checked the cultural terms on 2026-11-25: ዓይቢ was corrected to ኣጅቦ, and ጥሕሎ was removed.*

### Visual consistency rules (applied to every image and video prompt)

1. **Style:** cinematic historical realism with natural light, warm earth tones and soft film grain. No cartoon, fantasy or painterly-illustration look.
2. **Landscape and architecture:** authentic Tigray highlands (rocky ridges, stone terraces, dry-stone walls, sparse trees) and the homestead buildings described above. Nothing invented or from another region.
3. **Characters:** the same two descriptions from the table above, word for word, in every prompt. Generated against one approved character reference sheet.
4. **Clothing:** traditional dress only. Both brothers wear the white gabi in every shot.
5. **Period:** mid-20th century. **No modern elements**: no plastic, metal roofs, power lines, vehicles, phones, modern clothing or printed text.
6. **Night light:** a kerosene lantern and moonlight only. The sky moves steadily from dusk, through deep night, to dawn across the shots.

## 6. Shot plan (v2, before user test 1)

| # | Shot | Size | Reason it exists | ~s |
|---|---|---|---|---|
| 1 | Two similar homesteads (ህድሞ, ሳፁን, ኣጉዶ) far apart across the valley, mountain behind, dusk | Extreme wide | Place, and the distance between the brothers | 6 |
| 2 | A gathering: food is laid out on the መሶብ and people sit down, but ተስፋይ stays standing and does not celebrate | Medium | Love in action #1: he will not take part without his brother | 6 |
| 3 | ተስፋይ asks the people around him: "ወልደቻኣል ሓወይ ፀውዕዎ"; someone sets off to call him | Close-up | The request: he sends for his brother and waits | 6 |
| 4 | ወልደቻኣል arrives with his stick; only then does ተስፋይ sit beside him and join the celebration | Wide | The wait ends; they are always together | 6 |
| 5 | Hands: one brother gives the other a gursha | Close-up insert | Love without words | 5 |
| 6 | Dusk into night: they leave together under a lantern; ወልደቻኣል walks ተስፋይ home | Wide | The journey begins | 7 |
| 7 | At ተስፋይ's homestead: he will not let his brother go alone and turns back to walk him home | Medium | The loop begins: they take turns | 8 |
| 8 | At ወልደቻኣል's homestead, the moon high: now ወልደቻኣል turns back to walk ተስፋይ home | Medium | The loop repeats; the night deepens | 9 |
| 9 | Faces in lantern light on the path: "ተስፋይ ሓወይ!" / "ወልደቻኣል ሓወይ!" | Close-up | The heart of the film | 9 |
| 10 | The sky pales from night to dawn; the lantern still burns, and they still walk side by side | Wide | Night turns into dawn; they never said goodbye | 9 |
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
| Second native speaker | *pending* | | | |

## 8. User test 1: radio cut (narration over placeholder music, black screen)

**Status:** not yet run.

**Plan:** at least 3 people, in person or on Slack, including at least one Tigrigna speaker (to check the narration and names) and at least one non-Tigrigna speaker (to check the story through the subtitles alone). Questions:
1. In one sentence, what was the story about?
2. What did you feel at the end?
3. Which moment stayed with you?
4. Was anything confusing, too fast or too long?
5. Were the Tigrigna words and the names ወልደቻኣል and ተስፋይ pronounced correctly?

| Person (role, not name) | What they said | Insight |
|---|---|---|
| | | |

**What changed in the storyboard because of it:** —

## 9. User test 2: near-final cut

**Status:** not yet run.

| Person (role, not name) | What they said | Insight |
|---|---|---|
| | | |

**What changed because of it:** —

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
