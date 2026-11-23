# video-digest

A Claude skill for transcripts of videos, podcasts and talks, on any topic. Paste the transcript, activate the skill, and you get back in one go:

- **Accuracy score (1-10)**: key claims checked with web search against primary sources, including whether they are still true today
- **Usefulness score (1-10)**: judged for you, from what Claude knows about you (profile, memory, projects), not for people in general
- **Numbered summary**: the content in 1-2 line points, each with a verdict: True, Doubtful, False, Unverified or Opinion
- **What you can use**: 2-3 concrete things to try or look into

Then you pick the points to dig into ("tell me more about 2 and 5") and the conversation continues from there, with the numbering kept.

## How it works

```
transcript ──► clean (sponsors, intros, filler removed) ──► find key claims ──► web search ──► verdict per point ──► scores ──► digest ──► deep dives on request
```

| Step | What happens |
|---|---|
| 1. Clean | Drops sponsor reads, intros, outros, calls to subscribe and filler without mentioning them; fixes names mangled by auto-transcription |
| 2. Check | Searches the claims the content stands on, prefers primary sources, flags outdated information and the usual distortions (numbers out of context, sponsor products as neutral advice, opinion as fact) |
| 3. Usefulness | Judges what you could actually apply, from your profile, memory and projects |
| 4. Digest | Two scores, numbered summary with verdicts, what you can use |
| 5. Deep dives | Develops the points you pick, with new searches and concrete next steps |

## Output example

```
Accuracy: 7/10 - main facts check out, two figures are outdated
Useful for you: 8/10 - the tool in point 3 fits a project you are working on

Summary
1. [True] ...
2. [Doubtful] ... (the price was right in 2025, today it is ...)
3. [Opinion] ...

What you can use
- ...

Tell me which points to dig into.
```

The skill is written in English but answers in your language, whatever the language of the transcript.

## Requirements

Claude with skills enabled and web search: claude.ai, the Claude desktop app or Claude Code. Memory or a profile makes the usefulness score personal; without them it judges for a curious generalist. No scripts and no connectors needed.

## Installation

See the [main README](../README.md#installation). The skill is a single `SKILL.md`, so on claude.ai you can also create it directly from the file's content.

## License

[MIT](../LICENSE).
