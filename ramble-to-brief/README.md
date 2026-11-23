# ramble-to-brief

A Claude skill for handing off a job you don't want to supervise step by step. You talk freely about what you want (typed or dictated by voice, in any order), the skill turns it into a complete brief, shows you what it understood, asks every open question in a single round, and only after your explicit go does Claude run the job on its own until it is finished.

It sits between two ways of working:

- **Fully interactive** (questions all along the way): good when the idea is still vague, but you have to stay at the keyboard.
- **Fire and forget** (one prompt, no questions): fast, but you never know whether the prompt had everything Claude needed or whether it understood you.

ramble-to-brief keeps the checks of the first and the autonomy of the second: one round of questions at the start, then no more interruptions.

## When to use it

- Long research (comparing models, prices and licences)
- Building or testing a skill or a feature end to end
- Batch work on many files
- Large documentation or reorganisation jobs
- Anything you want to launch and find finished later

If the project is still vague and you want to explore options together, a conversational design process is a better fit.

## How it works

```
ramble ──► brief (7 parts + limits) ──► "what I understood" + open questions ──► your answers ──► final brief ──► GO ──► autonomous work ──► checks ──► report
```

| Step | What happens |
|---|---|
| 1. Listen | Reads the ramble, attachments and the context you already keep (CLAUDE.md, project docs, memory) |
| 2. Brief | Writes the brief in seven parts (see below) plus a Limits line |
| 3. Check | Shows "What I understood" in its own words, the names it interpreted from the ramble, and all open questions, each with the default it would use |
| 4. Go | Applies your answers, shows the final brief, saves it as `BRIEF.md` if you work in a folder or repo, and asks for an explicit go |
| 5. Work | Works alone until done; stops only for something listed under Limits |
| 6. Report | Result, how it was checked, decisions taken alone, what did not work |

## The brief

1. **Goal and why**, with the real numbers
2. **Quality bar**: what excellent looks like, in checkable terms
3. **Tools and inputs**: what exists and must be used, plus permission to find more
4. **Freedom**: what Claude decides alone and what must stay as stated
5. **Checks**: how the work is verified before it is called done
6. **Delivery**: where the result goes and what comes back to you
7. **The goal in one sentence**

**Limits**: actions that need your approval even after the go. Defaults if you name none: spending beyond what the brief states, publishing or pushing anything public, deleting or overwriting your files, anything that cannot be undone.

## Dictated rambles

Voice dictation produces long, unstructured text. The skill reads it with a few habits:

- Tool and project names mangled by transcription are matched against what it knows from your context, and every interpreted name is shown to you, never swapped silently.
- "I don't remember what it's called" plus a description: it identifies the thing and names it back.
- When you refine an idea further on, the later statement wins; real conflicts become questions.
- "Only" and "just" are often loose: when taking them literally would rule out something obviously useful, it asks.
- "First this, then we'll see about the rest" sets the scope of the current job.
- Analogies ("like that Photoshop tool", "like my other skill") are turned into concrete behaviour.

## Requirements

Claude with skills enabled: claude.ai, the Claude desktop app or Claude Code. No scripts and no connectors needed.

## Installation

See the [main README](../README.md#installation). The skill is a single `SKILL.md`, so on claude.ai you can also create it directly from the file's content.

## License

[MIT](../LICENSE).
