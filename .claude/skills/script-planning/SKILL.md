---
name: script-planning
description: Plan and write the narration script and shot list for an explainer video. Use first, before any voice, image, or video generation, whenever the user asks for an explainer, video, lesson, or animated walkthrough of a topic.
---

# Script planning

## 1. Find the one idea
Write one sentence: what should the viewer understand at the end that they did not at the start? Cut everything that does not serve it.

## 2. Outline as a chain of questions
Each beat raises the question the next beat answers. A typical arc: a familiar observation, the naive explanation, why it fails, the better model, what it predicts, and a closing image that returns to the opening.

## 3. Write the narration
Narrate like a university professor and follow the voice rules in CLAUDE.md. Aim for about 140 words per minute of runtime. Give each paragraph an id (p01, p02...) and an emotion tag in brackets for the TTS skill, e.g. [curious], [gently amused], [quiet, reflective]. Use this exact format in script.md, which the TTS and critic scripts parse:

```
## p01 [curious]
Paragraph text...

## p02 [quiet, reflective]
Paragraph text...
```

## 4. Self-audit before handing off
Search the draft for runs of three or more sentences under eight words, more than one figure in a paragraph, the words "let's", "here's", "dive", "landscape", "crucial", "delve", and any dash used as punctuation. Rewrite every hit.

## 5. Shot list
Write shots.yaml with one entry per beat:

```yaml
- id: s01
  vo: p01            # paragraph id in script.md
  kind: generated    # generated | manim | html | clip | still
  motion: low        # high routes to Seedance
  prompt: "..."      # for generated and still shots
  refs: [ref_style, ref_sky]
  notes: "..."
```

Every visual should show what the narration says at that moment, not decorate it.
