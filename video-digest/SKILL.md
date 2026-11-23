---
name: video-digest
description: Digest a pasted video or podcast transcript on any topic - fact-check score, usefulness-for-me score, numbered summary with a verdict per point, what I can use - then deep-dive into the points I pick.
---

# video-digest

The user pastes the transcript of a video (YouTube or similar), a podcast or a talk, on any topic. This skill answers the questions they would otherwise ask every time: is it true, is it useful to me, what does it say, what can I do with it. Then it lets them pick points to explore further.

This skill is written in English, but always answer in the user's language, even when the transcript is in another language.

## Principles

- Works for any topic: tech, health, finance, history, DIY, news, anything. Do not assume the subject.
- Verify, do not trust the speaker. Confidence, view counts and "experts say" are not evidence.
- Usefulness is about this user, not people in general. Judge it from what you know about them.
- Short and scannable. The digest is a starting point; depth comes when the user asks for it.
- Never invent sources. If you could not verify something, say so.

## Step 1: Clean the transcript

Auto-generated transcripts are messy. Silently drop everything that is not content: sponsor reads, ads, "like and subscribe", intros and outros, channel promotion, greetings, filler, repetitions. Do not mention what was removed.

Read through transcription errors: names of products, people, tools and places often come out as similar-sounding words. Fix them from context and, if you are unsure, check with a search. If an interpretation changes the meaning of a point, write the corrected name in that point.

If the transcript seems cut off or is clearly only part of the video, say so in one line at the top.

## Step 2: Find the claims and check them

List the claims the content stands on: facts, figures, dates, prices, product features, "X does Y", studies cited, predictions presented as facts. Ignore trivial ones.

Check the important ones with web search:

- Search each key claim separately; prefer primary sources (official docs, papers, government or company pages, original data) over blogs and other videos.
- Videos age. Check whether what is said is still true today (prices, versions, availability, laws, rankings) and note it when something was true at the time but is outdated now.
- Watch for the usual distortions: correct facts with a wrong conclusion, numbers out of context, cherry-picked studies, a sponsor's product presented as neutral advice, opinion presented as fact.
- Scale the effort: a short, simple video needs a few searches; a dense one with many factual claims needs more. Stop when every claim in the summary has a verdict you can defend.

Give each summary point one verdict:

- **True**: confirmed by reliable sources
- **Doubtful**: partly true, exaggerated, outdated, or sources disagree
- **False**: contradicted by reliable sources
- **Unverified**: could not be checked
- **Opinion**: a personal view or advice, not a factual claim (say briefly if it is reasonable)

## Step 3: Judge usefulness for this user

Use what you know about the user: their profile, memory, preferences, ongoing projects, the context files they keep. Ask yourself what in this content they could actually apply, learn from, or should be careful about, given their work, projects, tools and interests.

If you know nothing relevant about them, judge for a curious generalist and say so in the score line. Never mention private details unnecessarily; just let them shape the judgment.

## Step 4: Write the digest

Use exactly this structure, translated into the user's language:

```
**Accuracy: X/10** - one line on why
**Useful for you: X/10** - one line on why

**Summary**
1. [Verdict] Point in 1-2 lines, with the correction or the up-to-date fact if the verdict is not True
2. [Verdict] ...
...

**What you can use**
- 2-3 concrete things the user could try, apply or look into, tied to their situation

Tell me which points to dig into.
```

Scoring:

- **Accuracy**: 9-10 everything important checks out; 7-8 small errors or outdated details; 5-6 a mix of right and wrong or misleading framing; 3-4 mostly wrong or misleading; 1-2 false or harmful. Weigh claims by how much the content depends on them, not by count.
- **Useful for you**: 9-10 directly applicable to what the user is doing now; 7-8 relevant to their interests or work; 5-6 interesting but no clear use; 3-4 marginal; 1-2 nothing for them.

Summary rules:

- Number every point, so the user can refer to them ("dig into 2 and 5").
- Follow the logic of the content, not the order of the sentences; merge repetitions.
- Usually 5-12 points depending on length and density.
- If the content is wrong or misleading somewhere that could cost the user money, health or time, say it plainly in the point.

If "What you can use" would be empty, write one line saying nothing applies to them, rather than inventing uses.

Cite the sources used for the verdicts as the interface does for web results; do not paste long quotes.

## Step 5: Deep dives

When the user picks points ("tell me more about 3", "1 and 4"), develop each one:

- What the speaker said, what is actually true, and why the verdict.
- More detail, with new searches if needed: how it works, numbers, alternatives, risks.
- How it applies to the user specifically, with concrete next steps if they want to act on it.

Keep the original numbering for the rest of the conversation, so the user can keep referring to points. From here the conversation is free: follow wherever the user takes it.
