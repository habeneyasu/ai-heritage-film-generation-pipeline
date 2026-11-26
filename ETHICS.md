# ETHICS.md

## 1. Family authorization and consent

| Person | Relation | How they appear | Permission | Date | Form |
|---|---|---|---|---|---|
| My father | Storyteller and grandson of ወልደቻኣል; the custodian of this story | Not shown and not voiced; his story is retold in my words | **Consent given.** He agreed that I may make and publicly post an AI-made film of our family story about ወልደቻኣል and ተስፋይ, using their names, narrated by an AI voice | 2026-11-25 | Verbal, reported by the author. *The evidence of his permission is kept privately by the author.* |
| ወልደቻኣል | My great-grandfather (deceased) | An **imagined** AI-generated character; no photographs exist or were used | **Family authorization** (see below) | 2026-11-25 | As above |
| ተስፋይ | His brother (deceased) | An **imagined** AI-generated character; no photographs exist or were used | **Family authorization** (see below) | 2026-11-25 | As above |

**Family authorization:** my father, the family's storyteller and custodian of this story, gave permission for its retelling and for imagined AI depictions of ወልደቻኣል and ተስፋይ. This is family authorization, not direct consent from the deceased.

**Likeness:** no photographs, recordings or descriptions of real faces are given to any model. The faces are invented from a written character description.

**Voice:** the narration uses a stock Gemini TTS voice. No real person's voice is cloned or imitated. The narration is my own words, and the quoted lines (ሓወይ, ፀውዕዎ) are the words the family remembers them saying.

## 2. Labelling and AI disclosure

- A visible end card in the film (about 3 s, added in code) says the film was made with AI.
- The public post has the platform's AI-content disclosure label switched on.
- The post text says the images, motion, music and narration were generated with AI models.
- **Fictional likeness statement**, in the post text and the README: *"The characters are fictional AI-generated interpretations based on written family recollections. They are not verified historical likenesses."* This keeps viewers from reading the generated faces as authentic photographs.
- Watermarks and provenance metadata are never removed on purpose, and the committed model outputs (images, clips, narration, music) keep whatever the providers attached. But assembly re-encodes everything into one MP4, so file-level provenance (C2PA manifests) does not carry over into the final film, and mixing and compression may weaken signal-level watermarks such as SynthID in Gemini's audio. The film's disclosure therefore rests on the end card, the platform label and the post text above.

## 3. Licences, provider terms and output rights

Three different things are tracked separately:
- the **model licence** (the terms for using the weights),
- the **provider's terms** (the terms of the service that runs the model),
- the **rights in the generated outputs**.

An open-source model licence does not by itself guarantee that every generated output is free of third-party rights claims. That is why section 5 adds a review before publication.

*Checked on 2026-11-26 against the model cards and provider terms linked below. The Kaggle terms were read in full by the author (the page does not load without a browser).*

| Stage | Model / tool | Model licence | Provider terms | Output rights |
|---|---|---|---|---|
| Script, translation | None | Not used: the story and the narration were written with the author, not generated | Not applicable | Not applicable |
| Narration | Gemini 3.8 Flash TTS | Proprietary (API access only) | [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms); the free tier may use content to improve Google's products (see section 4) | Google "won't claim ownership" of generated content, may generate similar content for others, and makes the user responsible for its use (archived terms of 25 Sep 2025; to re-check against the live page) |
| Keyframes, references | FLUX.2 klein 4B (FLUX.1 schnell only tested, E03) | Apache 2.0 ([model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)); the 9B version is non-commercial and **is not used** | [Workers AI privacy and data use](https://developers.cloudflare.com/workers-ai/platform/privacy/): inputs and outputs are Customer Content, Cloudflare does not use them to train models | Customer Content: "You own, and are responsible for, your Customer Content"; model licence terms apply between us and the model provider |
| Moving shots | Wan 2.2 TI2V-5B (Diffusers weights) | Apache 2.0 ([model card](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers)) | **Kaggle is the provider**: weights downloaded from Hugging Face and run inside a private Kaggle notebook. [Kaggle Terms of Use](https://www.kaggle.com/terms) (effective 22 June 2025): the Services may be used only for "your own internal, personal, non-commercial use" | Apache 2.0 places no restriction on outputs. Because the clips were made on Kaggle, the film is shared for **personal, non-commercial** purposes only; any commercial use would need the terms reviewed again. Ownership stays with us: the uploads and notebooks are private ("Personal User Submissions"), and Kaggle's licence is only to operate the service; "your ownership in User Submissions is not affected" (section 9) |
| Music | ACE-Step 1.5 turbo | Code MIT ([GitHub](https://github.com/ace-step/ACE-Step-1.5)); weights tagged MIT on the [model card](https://huggingface.co/ACE-Step/Ace-Step1.5), but the weights repo has no LICENSE file ([open discussion](https://huggingface.co/ACE-Step/Ace-Step1.5/discussions/27)) | **Kaggle is the provider**, as above (personal, non-commercial use) | The model card says outputs may be used commercially, but because they were made on Kaggle we treat them as personal, non-commercial. This is **not** treated as a guarantee of copyright clearance for every track; see the originality check in section 5 |
| Assembly | FFmpeg | LGPL / GPL (tool only) | Not applicable (runs locally) | Not applicable |

## 4. Private data

- **Model providers:** the free Gemini API tier may use content sent to it to improve Google's products, while paid-tier content is not used this way. Only what the film needs is sent: first names, the story and generic descriptions. No surnames, exact village, family photos or contact details are sent to any endpoint.
- **Region:** kept vague ("a highland village in Tigray").
- **User-test participants:**
  - Feedback is recorded without names or unnecessary identifying details. Each person is listed only by a general role, such as "Tigrigna speaker" or "non-Tigrigna speaker".
  - Details such as relationship, age range or diaspora status are left out, because in a small community a combination of them could identify someone.
  - Participants are told before they give feedback that it may be included in the public project documentation.

## 5. Review before publication (originality and representation)

Before the film or any asset is published, every generated output is reviewed:

| Check | Applies to | What is checked |
|---|---|---|
| Music originality | Score candidates and the final score | The score is reviewed for recognisable similarities to known protected compositions, particularly melodies and distinctive hooks. Any suspicious track is rejected and regenerated with a different seed and prompt. This review reduces risk but does not guarantee copyright clearance. |
| Cultural representation | Keyframes and video shots | Clothing, homes, food and customs are shown respectfully and accurately, following the visual rules in DESIGN.md. There are no caricatures and no elements from other cultures or periods. |
| Unintended marks | All images and video | There is no unintended text, logos or watermarks beyond the expected model provenance (SynthID, C2PA). |

The result of each review is noted in EXPERIMENTS.md or FAILURES.md, together with what was regenerated.

## 6. Style and cultural respect

- The style is described by its qualities (for example cinematic, warm, soft lantern light) and never by naming a living artist.
- Cultural details (white gabi, ህድሞ, ሳፁን, ኣጉዶ, ኣጅቦ, ሕምባሻ, መሶብ) were checked against the author's family knowledge and recollections. Native-speaker validation of the Tigrigna narration and names is recorded separately, in DESIGN.md (section 7, the Tigrigna sample check, and sections 8–9, the user tests).
- The film leaves out recent political events. It is about two brothers and their love.
