# RSK video rules (standing, apply to every video)

These override anything looser in the pipeline skills. Each one fixes a real problem from the RSK "What we do" explainer (October 2026); see "Why" at the end.

## Before anything else

Ask only the questions the brief leaves open, each with a suggested default. Then send a script plus a one-line-per-shot list. Generate nothing until the reviewer approves.

## RSK guardrails

- No recovery percentage, no "we sue insurers," and AI is never the pitch.
- The only allowed money claim: contingency fee, paid only from recoveries.
- Scope is commercial and managed care. Say "payer contract." Never Medicaid.
- Demo data only (RSK Health Demo Provider). No real client, customer or patient details on any screen (HIPAA and confidentiality).
- No totals or stats that undersell the offer.
- When selling a service, show the RSK team doing the work, not the customer doing it themselves.

## Content

- Every frame carries information specific to healthcare billing. If swapping the logo makes it fit a bank or law firm, it's generic. Redo it.
- Show the core idea as drawn motion graphics (contract rate vs. 835 payment, documents, diagrams). Use generated scenes only for setting and story.
- Use real domain details: front desk, payer portal, paper EOBs, headset, exam room door.
- Banned props: coins, magnifying glasses, fountain pens, circled calendars, glowing glass or holograms, whiteboards, handshakes.
- Give the story a protagonist with a visible face. Don't shoot everyone from behind.

## Visual style

- Default: flat illustration plus data cards in the same style (Stripe/Ramp explainer look). Avoid moody "cinematic corporate" (dark rooms, golden glow, heavy blur); it reads as AI slop. Reference: `examples/rsk-explainer-v2/style/` and `refs/`.
- If a different style is wanted, make 3 cheap style frames of one scene and let the reviewer pick.
- Brand navy and orange only in graphics, titles and on-screen UI. Never in sets, furniture or clothing. Data cards: navy for amounts, orange only for the gap.
- Lock one character sheet first; every scene references it. Keep recurring traits (glasses, hair, clothes) in every shot. Side characters never copy the protagonist's outfit.
- No readable text inside generated images. Draw all words and numbers in code.
- Vary shots (wide, medium, few close-ups), lighting and focus.
- Graphics about 70% of frame width so they read on phones. Sentence case everywhere.

## Physical realism (check every still and clip)

- A screen is visible only from the side it faces. Anyone behind a monitor sees a plain gray back. Prefer over-the-shoulder or three-quarter angles.
- No sliding, folding or flipping paper; hands near paper stay still. Screens keep their direction. Push-ins 10% or less.
- If a clip's motion looks wrong, use the still with a drawn push-in instead of paying for a retake.

## Production

- Seedance for about 5 story scenes only. Everything else drawn in code (Manim/ffmpeg), which is free.
- Voice: Edge TTS `en-US-AndrewNeural` (config default). No music, no sound effects, no Gemini or ElevenLabs voice.
- Captions burned in: large, white on an opaque navy box, current word in orange. Also export an .srt.
- Run the critic on every full draft.

## Budget and gates

- Before spending, check the OpenRouter KEY's own credit limit. It is separate from account credit. Say so if it's below the brief's cap.
- Log every paid call to `work/<slug>/spend.jsonl`. Report running spend at every gate. Stop at the cap and show the work.
- Stop for approval at each gate: shot list, character sheet, scene stills, test clips, full draft. Before generating, confirm the shot file has no duplicate or stale shots.
- Rough costs: illustrated still about $0.14, Seedance clip $1.15 to $1.40, a full 90-second video about $11.

## Why

| What went wrong | Rule it produced |
| --- | --- |
| First stills were moody navy rooms, coin stacks and magnifiers that could fit any bank | Swap-the-logo test, banned props, flat illustration |
| Brand colors painted on walls, lamps and chairs | Brand colors only in graphics and UI |
| Everyone shot from behind, so no one to follow | Protagonist with a visible face |
| The administrator found and fixed the gap herself | Show the RSK team doing the work |
| Generated paperwork had mirrored, garbled text | No text in generated images |
| A patient saw a screen on the back of the monitor | Screens visible only from the side they face |
| Seedance made folders and papers move unnaturally | No paper motion; drawn push-in instead |
| A $1,416 total made the offer look small | No totals that undersell |
| The key hit its $10 limit even after the account was topped up | Check the key's own limit first |
| Gemini voice and sound effects sounded off | Edge voice only, no music or effects |
