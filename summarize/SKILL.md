---
name: summarize
description: When the user sends a link (article, blog post, page) to summarize, fetch it and reply with a structured summary in the user's language.
---

# Summarize

Use this skill when the user sends a URL, alone or with words like "summary", "riassunto", "riassumi".

## Steps

1. Fetch the page with WebFetch. Ask for the full content: main thesis, key arguments, concrete examples, FAQ and conclusions. If the page is long or truncated, read on with the offset parameter before summarizing.
2. If the page cannot be fetched (blocked, login required), say so in one line and ask the user to paste the text. Never summarize from memory or guess the content.
3. Reply in the language the user writes in (Italian by default), whatever the language of the source.

## Output format

Start with a title line: the article title in quotes, then author, site and publication date in parentheses when available.

Then, in this order and skipping any section the source does not have:

- **Main thesis**: 2-3 sentences on what the author claims and why.
- **Key arguments**: short list, one line each, with the bold label first.
- **Concrete examples**: short list of the cases or examples the source gives.
- **FAQ / caveats**: only if the source has them (costs, limits, objections).
- **Conclusion**: 2-3 sentences, including the practical takeaway.

## Style

- Direct and compact: the user reads on a phone, so aim for about one to two screens.
- Paraphrase in your own words. At most one short quote (under 15 words) per source, and only if the exact wording matters.
- No emoji, no preamble, no "here is the summary".
- Report only what the source says. Do not add your own opinion unless the user asks.
- Cite the source with the tool's citation format if available.
- If the user asks to go deeper on a point, fetch again with a prompt focused on that point.
