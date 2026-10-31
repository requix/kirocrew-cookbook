# Contributing to KiroCrew Cookbook

Thank you for contributing! This guide covers how to add or update recipes.

## Before you start

- **Test your recipe.** Every step should work on a fresh KiroCrew install.
- **Check the source.** If you mention a command, setting, or tool, verify it exists in the current KiroCrew version.
- **Keep it practical.** Recipes solve real problems. Skip the theory; show the steps.

## Adding a recipe

### 1. Create the file

Copy the template:

```bash
cp content/recipes/TEMPLATE.txt content/recipes/your-recipe-name.md
```

Use lowercase, hyphens, no spaces.

### 2. Fill in the frontmatter

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
  - KiroCrew running (see Your first hour)
---
```

### 3. Write the content

Structure:

```markdown
**Problem.** What goes wrong without this recipe. One paragraph.

## The key insight (optional)

If there's one thing to understand, put it here.

## Steps

### 1. First step

Explain what to do. Include a prompt example:

` ` `prompt
Tell KiroCrew to do the thing.
` ` `

### 2. Second step

Continue with numbered steps.

## What can go wrong

Common mistakes and how to fix them.
```

### 4. Register the recipe

Add your filename (without `.md`) to `content/recipes/meta.json`:

```json
{
  "title": "Recipes",
  "pages": ["existing-recipe", "your-recipe-name"]
}
```

### 5. Build and test

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

### 6. Open a PR

- One recipe per PR
- PR title: `docs: add recipe for <topic>`
- Include a screenshot if the recipe has visual output

## Style guide

### Voice

- Second person ("you"), not first ("I") or third ("the user")
- Present tense ("Run this command"), not future ("You will run")
- Direct instructions, not suggestions ("Run X", not "You might want to run X")

### Code blocks

- `prompt` — for things to say to KiroCrew
- `bash` — for terminal commands
- `python`, `json`, etc. — for code snippets

### Links

- Internal links use relative paths: `[Install](../start/install.md)`
- External links are allowed but keep them minimal

## Updating existing recipes

Same process, but note what changed in the PR description. Update the `updated` date in frontmatter.

## Questions?

Open an issue or ask in the KiroCrew community.
