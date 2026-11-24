# summarize

Send Claude a link and get a structured summary of the page, in your language.

## What it does

1. Fetches the page (WebFetch), reading on if it is long or truncated.
2. Replies with: title line (author, site, date), main thesis, key arguments, concrete examples, FAQ or caveats (only if the source has them) and conclusion.
3. Replies in the language you write in, whatever the language of the source.

## Rules

- If the page cannot be fetched, Claude says so and asks you to paste the text. It never summarizes from memory.
- Paraphrase only: at most one short quote (under 15 words) per source.
- No opinion of its own unless asked, no emoji, no preamble.
- Compact output, about one to two phone screens.

## Requirements

Claude with skills enabled and web fetch available. No scripts, no connectors, no credits.

## Usage

Paste a URL, optionally with "summary" or "riassumi".
