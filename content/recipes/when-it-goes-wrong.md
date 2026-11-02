---
title: When it goes wrong
description: What a loop, a blocked command, a drifted session and a dead gateway look like, and the fix for each.
category: Troubleshooting
difficulty: beginner
time: 10 min
surfaces: [dashboard, cli]
tags: [recovery, approvals, doctor]
updated: 2026-10-29
featured: false
---

**Problem.** It is looping on the same fix. A command got blocked. The session drifted off what you asked. This is the recipe nobody writes, and it is the one you reach for most.

Here is what each failure looks like and what to do.

## It is stuck in a loop

**Looks like:** it tries a fix, fails, tries almost the same fix, fails again. Three rounds, no progress.

**Do this:**

1. Stop it. Say so plainly:
   ```prompt
   Stop. This isn't working.
   ```
2. Make it step back, not patch again:
   ```prompt
   Don't try another small change. Tell me the root cause first, then propose a different approach.
   ```

A good agent switches tracks after two failures on its own. When it does not, this forces it.

## A command was blocked

**Looks like:** "this command is blocked by policy" or an approval prompt you did not expect.

**Know this first:** a block is a **decision**, not a bug. Kiro Crew checks every tool call at a safety gate. Some blocks are built in (deleting things, force-pushing to main). Some are your own rules. Some are just missing credentials.

**Do this:**

- **Read the reason.** The refusal says *why*. That tells you which of the three it is.
- **If it is missing credentials:** fix the credential, then retry. ("Run `aws sso login` first.")
- **If it is your own rule and you meant it:** good. The gate did its job.
- **If you genuinely want this one command:** approve it when it asks. An approval is for that one call, not forever.

**Never** ask it to rewrite the command to dodge the check. That is the one move that is always wrong.

## The session drifted

**Looks like:** you started on one task, three topics happened, now its answers are muddled by old context.

**Do this:**

```prompt
Reset this conversation — start fresh, forget the earlier context.
```

The tab stays, your transcript stays, but the agent gets a clean head. **First** copy out anything you still need — a path, a decision — because the agent will not see it after the reset.

## It won't start at all

**Looks like:** dashboard won't load, or every session errors.

**Do this:** go to a terminal and run the doctor.

```bash
kirocrew doctor
```

It walks your setup section by section and flags what is broken. Fix what it flags.

Common ones:

- **`kiro-cli not found`** — install it, open a new shell.
- **Login expired** — `kiro-cli login`.
- **Gateway not running** — `kirocrew gateway`.

## It did something you did not want

**Looks like:** it edited a file, ran a command, made a change you did not ask for.

**Do this:**

- **For a file:** ask for the diff and revert it.
  ```prompt
  Show me what you changed and undo it.
  ```
- **For git:** nothing is pushed to protected branches without you — that is blocked. Local changes you can reset.
- **Teach it the boundary:** turn the mistake into a rule so it never repeats.
  ```prompt
  Never edit config files without asking me first.
  ```
  That becomes a lesson. Next time it asks.

## Gotchas

- **Two failures is the signal.** If it has tried twice, do not let it try a third small patch. Make it change approach.
- **A block is information.** Read the reason before you react. It tells you which fix you need.
- **Reset loses the agent's context, not your transcript.** You can still read the old messages; the agent cannot. Save what matters first.
- **`kirocrew doctor` is the first move for any startup failure.** Not the last. Run it before you guess.

## What you learned

Loop → stop it, demand a root cause. Block → read the reason, never dodge it. Drift → reset, after saving what you need. Won't start → `kirocrew doctor`. And every mistake is a chance to teach it a rule so it does not happen twice.
