# session-handoff

A Claude skill for the moment you leave a long chat and know you will come back later. It writes a short recap file you attach to a brand new chat, so you do not have to resume the old, heavy one.

## Why

Every time you send a message, Claude re-reads the whole conversation. Anthropic keeps a cached copy of it on its servers so that this re-read is much cheaper, but the copy expires after a period of inactivity (in Claude Code on a subscription, one hour for the main conversation; five minutes with an API key). If you come back after it expired, the whole conversation is processed again at a higher price, and on a subscription it can use up your limits faster. Very long chats also tend to give worse answers.

For small chats none of this matters. For long ones, a short recap in a fresh chat is cheaper and cleaner than resuming the old one.

Exactly how claude.ai and the mobile app count the cache against your usage limits is not documented, so the skill does not depend on it: it is simply a good habit before a long pause.

## What you get

One Markdown file, about one page, in your language, with these sections:

| Section | Content |
|---|---|
| Resume prompt | One sentence to paste into the new chat |
| Written on | Date and time of the recap |
| Goal | What the work is meant to achieve |
| Decisions | Each decision, with the reason in one line |
| Current state | What is done, what is not, what was tried and failed |
| Files, links, commands | Everything needed to continue, with complete copyable commands |
| Open points | Open questions and unfinished tasks |
| Next step | The single next action |

## How it works

```
/session-handoff ──► re-read the chat ──► verify real state (if tools exist, read-only) ──► write recap ──► send the file
```

| Step | What happens |
|---|---|
| 1. Re-read | Goes through the conversation and the files, links and commands used |
| 2. Verify | Only where a shell or file tools exist: `git status`, `git diff --stat`, `git log -5`, checks that the paths mentioned exist, reads the current date and time, copies unfinished tasks. Nothing that changes state. In a plain browser or mobile chat this step is skipped |
| 3. Write | One short Markdown file, no emoji, no secrets |
| 4. Deliver | Sent as a file in the conversation, so you can download it from any device; if files cannot be created, the recap is written in the reply as one block to copy |

## Use

Run `/session-handoff`, or say that you are closing and coming back later. When you come back, open a new chat, attach the file and paste the resume prompt written at the top of it.

## What it does not do

- It does not save the recap to a repository, memory or any other place unless you explicitly ask.
- It does not update any skill or document.
- It does not run anything that changes state.

If something in the recap should stay for good, keep it in your own notes or documentation as you normally do: the recap is meant to be thrown away once you have resumed.

## Requirements

Claude with skills enabled: claude.ai, the Claude desktop app or Claude Code. No scripts and no connectors needed. The verification step uses a shell only where one is available.

## Installation

See the [main README](../README.md#installation). The skill is a single `SKILL.md`, so on claude.ai you can also create it directly from the file's content.

## License

[MIT](../LICENSE).
