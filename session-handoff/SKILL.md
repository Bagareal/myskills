---
name: session-handoff
description: Write a short handoff recap (.md) before leaving a long chat, so work can resume in a fresh session. Use when the user says they are closing or will be back later.
---

# session-handoff

The user is about to leave a long conversation and will come back later (for example in an hour). Instead of resuming the old, heavy chat, they want a compact recap file they can attach to a brand new chat.

This skill only produces the recap. It never saves, updates or commits anything anywhere else.

## When to use

- The user runs /session-handoff.
- The user says they are closing, taking a break, or coming back later and wants to continue the work.

## Steps

1. Re-read the whole conversation and the files, links and commands used in it.
2. Verify the real state, read-only, only if the tools exist in this session (a shell or file tools). If they do not exist (plain browser or mobile chat), skip this step and rely on the conversation alone.
   - In a git project: run git status, git diff --stat and git log -5, so the recap lists the files that really changed and the latest commits.
   - Check that every file, folder or path mentioned in the recap exists (ls, test -f). Fix or remove the ones that do not.
   - Get the current date and time, and write it in the recap.
   - If the session has an open task list, copy the unfinished tasks into Open points.
   - Never run anything that writes, restarts, deletes or changes state.
3. Write one Markdown file, in the language the user writes in, about one page long. Shorter is better: a long recap carries the same weight the user is trying to leave behind. Use no emoji.
4. Use exactly these sections:
   - **Resume prompt**: one ready-to-paste sentence for the new chat, for example: "Resume this work from the attached recap, starting from the next step."
   - **Written on**: date and time the recap was written.
   - **Goal**: what the work is meant to achieve, in 1-3 lines.
   - **Decisions**: each decision taken, with the reason in one line.
   - **Current state**: what is done, what is not, what was tried and failed (so it is not repeated).
   - **Files, links, commands**: everything needed to continue. Commands must be complete and copyable, with real values and a short note on what to replace if anything. No "..." and no generic placeholders.
   - **Open points**: unresolved questions, things waiting on the user, unfinished tasks.
   - **Next step**: the single next action.
5. Leave out anything that is not needed to continue: pleasantries, dead ends that do not matter, long explanations already understood.
6. Never put secrets, passwords or tokens in the recap. If one is needed, say where the user keeps it.
7. Deliver the file in the conversation (send it as a file) so the user can download it from any device. If files cannot be created in this chat, write the recap in the reply instead, in a single block ready to copy.
8. Finish with one line telling the user to attach the file to a new chat and paste the resume prompt.

## Do not

- Do not save the recap to a repository, memory or any other place unless the user explicitly asks.
- Do not update any skill or document.
- Do not ask a list of questions: write the recap from what is in the conversation, and mark anything unclear under Open points.
- Do not run any command that changes state during verification.
