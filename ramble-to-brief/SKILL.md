---
name: ramble-to-brief
description: Turn a free-form ramble about a job into a complete brief, show what was understood, ask all open questions in one round, then run the job autonomously after an explicit go.
---

# ramble-to-brief

The user talks freely about a job they want done: what they have, where they want to end up, ideas, references, constraints, in any order and often by voice. This skill turns that ramble into a complete brief, checks with the user that it was understood correctly, collects every missing piece in a single round of questions, and only then runs the job on its own until it is finished.

Use it for jobs the user wants to hand off and not supervise step by step: long research, building or testing a skill end to end, batch work on files, large documentation or reorganisation work, anything that can run for a long time once it is clear.

This skill is written in English, but always talk to the user in their own language, and write the brief in their language.

## Principles

- Nothing starts before an explicit go from the user. Showing the brief is not permission to start.
- Ask every question in one round, never scattered through the work. After the go, do not ask again unless a limit in the brief says so.
- Never invent facts the user did not give. If something is missing, it becomes a question or a stated default, never a silent assumption.
- Keep the user's own words for goals, names and numbers. Do not soften or reinterpret them.

## Step 1: Listen

Let the user ramble. If they attach files, links or references, read them now, because they are part of the ramble. If the message is very short and there is clearly nothing to build a brief from, ask them to tell you more about the job and wait.

Also read the context the user already keeps (CLAUDE.md, project docs, memory, the repo the job is about): many requirements are not repeated in the ramble because they are standing rules there.

Do not start any work in this step.

### Reading a spoken ramble

Rambles are often dictated by voice and come out as one long stream. Read them with these habits in mind:

- **Transcription errors.** Names of tools, projects and services can come out wrong (a product name spelled like a common word, a similar-sounding word in place of a technical term). Match them against the tools, skills and projects you know from the context. Never silently swap a name: list each one you interpreted under "What I understood".
- **Forgotten names.** "I don't remember what it's called" followed by a description means: identify it and name it back (for example a Photoshop tool described by what it does, or one of the user's own skills described by its steps).
- **Thinking out loud.** Ideas are corrected or refined further on in the same ramble. The later statement wins over the earlier one; if two parts really conflict, it becomes an open question.
- **Loose absolutes.** Words like "only", "just", "and that's it" often describe the main constraint, not a complete list ("it can only slide along the plane" may still allow rotating and scaling, as long as it stays on the plane). When an absolute would rule out something obviously useful, ask instead of applying it literally.
- **Order of work.** Sentences like "first I want to try this, then we think about the rest" set the scope of this job: the rest goes in the brief as a later step, not as part of the job.
- **Analogies.** "Like X in Photoshop" or "like my other skill" describe how something should behave. Turn the analogy into concrete behaviour in the brief and say which tool or skill you took as the model.

## Step 2: Draft the brief

Write the brief with these seven parts. Each part is short and concrete; skip nothing, and if a part is empty write what is missing.

1. **Goal and why**: what the user wants and why it matters, with the real numbers they gave (quantities, sizes, deadlines, budgets).
2. **Quality bar**: what an excellent result looks like, described in concrete, checkable terms ("every product keeps its logo readable", not "high quality"). Include references the user gave.
3. **Tools and inputs**: the files, tools, connectors and services that already exist and must be used, plus permission to look for others if useful.
4. **Freedom**: what Claude may decide on its own (approach, order, tools, changing the plan) and what must stay exactly as the user said.
5. **Checks**: how Claude verifies the work before calling it done, at least once against the quality bar, with concrete checks (run the code, open the file, compare with the reference).
6. **Delivery**: where the result goes (file, folder, repo, artifact) and what comes back to the user at the end (a summary, a link, a list of open issues).
7. **The goal in one sentence**: the whole job restated in a single sentence.

Add a **Limits** line: actions that always need the user's approval even after the go. If the user named none, propose these defaults: spending money or paid credits beyond what the brief states, publishing or pushing anything public, deleting or overwriting the user's files, anything that cannot be undone.

## Step 3: Show what was understood and ask

Show the user the brief, followed by two sections:

- **What I understood**: 3 to 4 lines in your own words, not copied from the brief, so the user can spot a misunderstanding at a glance. Add the names you interpreted from the ramble ("you said X: I took it as Y") and the standing rules you picked up from the context files.
- **Open questions**: everything that is missing or ambiguous, numbered. For each one, say what you would do if they do not answer ("No format given: I would use 16:9"). Group related points; do not ask about things that do not change the result.

When the open questions are multiple choice, use a form (AskUserQuestion: up to 4 questions per form; the user can always type another answer). When they need free text, list them in chat and let the user answer all of them in one message.

If nothing is missing, say so explicitly instead of inventing questions.

## Step 4: Update and ask for the go

Apply the user's answers and corrections to the brief. Questions they did not answer take the default you stated. Show the final brief (or only the parts that changed, if it is long) and ask one clear question: start now?

If the answers changed the job substantially, repeat Step 3 once for the new points only.

If the user works in a folder or repo, also save the final brief as `BRIEF.md` there, so it can be read again during the work.

## Step 5: Run the job

After the go, work on your own until the job is done:

- Follow the brief. Where it leaves room, decide yourself and note the decision for the final report.
- Do not ask questions. If you hit a gap, take the most reasonable option consistent with the brief and record it.
- Stop and ask only for something listed under Limits, or if the job turns out to be impossible as briefed (say why and what the options are).
- Run the checks from part 5 before declaring the work finished. If a check fails, fix and check again; do not deliver something that fails its own checks without saying so.

## Step 6: Report

Deliver as stated in part 6, then give a short report:

- what was done and where the result is
- how it was checked and the outcome
- decisions taken on your own and assumptions made
- what is not done or did not work, said plainly

If the user corrected the work during this job in ways that should hold every time, list those corrections and propose how the brief template or this skill could change; change nothing until the user says which to keep.