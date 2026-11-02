# Contributing to Kiro Crew Cookbook

Thank you for contributing! This guide covers how to add or update recipes.

## Ways to contribute

| What | How |
|------|-----|
| Found a typo? | [Open a bug report](https://github.com/requix/kirocrew-cookbook/issues/new?template=bug_report.yml) or submit a PR |
| Recipe doesn't work? | [Open a bug report](https://github.com/requix/kirocrew-cookbook/issues/new?template=bug_report.yml) with Kiro Crew version |
| Have a content idea? | [Suggest content](https://github.com/requix/kirocrew-cookbook/issues/new?template=suggest_content.yml) |
| Want to write a recipe? | Fork, write, and open a PR (see below) |

## Before you start

- **Test your recipe.** Every step should work on a fresh Kiro Crew install.
- **Check the source.** If you mention a command, setting, or tool, verify it exists in the current Kiro Crew version.
- **Keep it practical.** Recipes solve real problems. Skip the theory; show the steps.

## Adding a recipe

### 1. Fork and clone

```bash
# Fork via GitHub, then:
git clone https://github.com/YOUR_USERNAME/kirocrew-cookbook.git
cd kirocrew-cookbook
```

### 2. Create the file

Copy the template:

```bash
cp content/recipes/TEMPLATE.txt content/recipes/your-recipe-name.md
```

Use lowercase, hyphens, no spaces.

### 3. Fill in the frontmatter

Every recipe needs this exact frontmatter:

```yaml
---
title: Your recipe title           # Max 60 chars
description: One sentence summary  # Max 140 chars
category: Memory                   # One of: Memory, Automation, Agents, Integration, Debugging
difficulty: beginner               # beginner, intermediate, or advanced
time: 15 min                       # Estimated time
surfaces: [dashboard, cli]         # Where it works: dashboard, cli, channels
tags: [memory, lessons]            # 2-5 searchable tags
updated: 2026-10-29                # ISO date
featured: false                    # Only maintainers set this
prerequisites:                     # Optional, list of things needed first
  - Kiro Crew running (see Your first hour)
---
```

### 4. Write the content

Structure:

```markdown
**Problem.** What goes wrong without this recipe. One paragraph.

## The key insight (optional)

If there's one thing to understand, put it here.

## Steps

### 1. First step

Explain what to do. Include a prompt example:

` ` `prompt
Tell Kiro Crew to do the thing.
` ` `

### 2. Second step

Continue with numbered steps.

## What can go wrong

Common mistakes and how to fix them.
```

### 5. Register the recipe

Add your filename (without `.md`) to `content/recipes/meta.json`:

```json
{
  "title": "Recipes",
  "pages": ["existing-recipe", "your-recipe-name"]
}
```

### 6. Build and test

```bash
cd build/preview
python3 build.py
```

The build validates:
- All required frontmatter fields
- Title under 60 chars, description under 140
- Valid difficulty and surfaces
- No broken internal links
- Every `.md` file is listed in a `meta.json`

Fix any errors before committing.

### 7. Open a PR

```bash
git checkout -b recipe/your-recipe-name
git add .
git commit -m "docs: add recipe for your-topic"
git push origin recipe/your-recipe-name
```

Then open a PR on GitHub.

**PR guidelines:**
- One recipe per PR
- PR title: `docs: add recipe for <topic>`
- Include a screenshot if the recipe has visual output

## Fixing typos and errors

For small fixes:

1. Fork the repo
2. Edit the file directly on GitHub or locally
3. Open a PR with title: `fix: typo in <page-name>` or `fix: correct <what>`

No need to run the build for typo fixes — CI will validate.

## Style guide

### Brand name

Always write **Kiro Crew** as two words. Never "KiroCrew" (no space).

| Wrong | Right |
|---|---|
| KiroCrew is running | Kiro Crew is running |
| Install KiroCrew | Install Kiro Crew |
| Build your own KiroCrew app | Build your own Kiro Crew app |

Exceptions that stay as-is: the CLI command (`kirocrew`), package name (`kirocrew`), and anything inside a code fence or backtick span — those are identifiers, not the product name. GitHub URLs that contain `KiroCrew` as the repo name also stay unchanged.

The build enforces this: `cd build/preview && python3 build.py` fails with a clear error if your prose or frontmatter uses "KiroCrew".

### Voice

- Second person ("you"), not first ("I") or third ("the user")
- Present tense ("Run this command"), not future ("You will run")
- Direct instructions, not suggestions ("Run X", not "You might want to run X")

### Code blocks

- `prompt` — for things to say to Kiro Crew
- `bash` — for terminal commands
- `python`, `json`, etc. — for code snippets

### Links

- Internal links use relative paths: `[Install](../start/install.md)`
- External links are allowed but keep them minimal

## Updating existing recipes

Same process, but note what changed in the PR description. Update the `updated` date in frontmatter.

## Code of Conduct

Be kind. Be helpful. Assume good intent.

## Questions?

- [Open an issue](https://github.com/requix/kirocrew-cookbook/issues)
