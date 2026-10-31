---
title: Teach it a skill
description: Write a project-local skill once, so the agent follows your method every time.
category: Skills
difficulty: beginner
time: 20 min
surfaces: [dashboard, cli]
tags: [skills, steering]
updated: 2026-10-29
featured: false
prerequisites:
  - KiroCrew running (see Your first hour)
  - A project folder the session works in
---

**Problem.** You keep explaining the same procedure every chat. "Review PRs this way." "Write in my voice, not AI voice." A lesson is one line; this is a whole method. That is what a **skill** is for.

A skill is a markdown file with steps. KiroCrew reads it when the task matches. You write the method once; it follows it every time.

## Skill vs lesson vs steering

Three ways to teach it. Pick the right one.

| You have | Use | Lives in |
|---|---|---|
| A one-line rule ("always use SSH") | A **lesson** | memory |
| A whole procedure ("how I review a PR") | A **skill** | `.kiro/skills/<name>/SKILL.md` |
| Facts about this project ("our stack, our conventions") | **Steering** | `.kiro/steering/*.md` |

This recipe is the skill.

## Project-local vs global

A skill can live in two places:

- **This project only:** `<project>/.kiro/skills/<name>/SKILL.md` — loads only when this project is open.
- **Every project:** `~/.kiro/skills/<name>/SKILL.md` — loads everywhere.

On a name clash, the project one wins. Start project-local. Promote to global only when you reuse it across repos.

## Steps

### 1. Make the folder and file

A skill is a folder with one required file, `SKILL.md`:

```tree
<project>/.kiro/skills/pr-review/
  SKILL.md
```

### 2. Write the SKILL.md

The top block (the frontmatter) is what matters. `name` must match the folder. `description` is when to use it.

```markdown
---
name: pr-review
description: Review pull requests for code quality, security, and test coverage.
---

## Review checklist
1. Check for injection risks and exposed secrets.
2. Verify edge cases and failure modes.
3. Confirm new code has tests.
4. Flag unclear naming.
```

That is a working skill. Steps in plain markdown.

### 3. Let it load

A skill loads automatically when a request matches its `description`. It is also a slash command — `pr-review` becomes `/pr-review`.

```prompt
/pr-review focus on the auth changes
```

Text after the command is passed in as extra context.

### 4. Keep big docs separate

Short skill in `SKILL.md`. Long reference material goes beside it in a `references/` folder — KiroCrew loads those only when the steps point to them. This keeps the skill fast to read.

```text
pr-review/
├── SKILL.md
└── references/
    └── security-checklist.md
```

## Verify

- Open the project. Ask for the task the skill covers ("review this PR").
- It should follow your steps without you pasting them.
- Type `/` and your skill name — it should show as a command.

## Gotchas

- **`name` must match the folder name.** Lowercase, numbers, hyphens. Max 64 chars. A mismatch means it will not load.
- **The `description` is the trigger.** Vague description, no auto-load. Write it as *when to use this*, not *what it is*.
- **Rename = rename the folder.** The skill name follows the folder. Change the folder, the frontmatter `name`, and they must still match.
- **Discovery is at session start.** Add a skill, then start a new chat session so it gets picked up.
- **A skill is a method, not a fact.** If it is one line, it is a lesson. If it is "what our project is", it is steering. Do not force everything into skills.

## A real one

This cookbook was written with a project-local skill called `authentic-voice`. It holds the rules for one writing voice — plain, honest, no AI filler — so every page sounds the same without re-explaining the voice each time. That is the pattern: a repeatable method, written once, in `.kiro/skills/`.

## What you learned

A skill is a markdown procedure KiroCrew follows when the task matches. Start project-local. Keep the body short, push long docs to `references/`. Match the folder name and write a trigger-shaped description.
