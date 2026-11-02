---
title: Kiro Crew Cookbook
description: "One page per real task: problem, steps, verify, gotchas."
hero: Recipes for running Kiro Crew for real
paths:
  - id: new
    label: New to Kiro
    title: Start from zero
    summary: You have not used any Kiro product yet. Install everything, step by step, then do one real task.
    pages: [start/install, start/first-hour, find/dashboard-map, concepts/how-it-fits]
  - id: kiro
    label: I use Kiro CLI or IDE
    title: Bring your setup
    summary: You already have steering files, agents, skills and MCP servers. See what carries over and what changes.
    pages: [start/bring-your-kiro-setup, concepts/how-it-fits, recipes/teach-it-a-skill]
  - id: deeper
    label: Kiro Crew is running
    title: Go deeper
    summary: It works. Now learn what keeps it safe, when to give a job its own crewmate, and how to feed it your docs.
    pages: [concepts/security, concepts/crewmates, concepts/knowledge-base, recipes/make-it-remember]
  - id: build
    label: I want to extend it
    title: Build on it
    summary: Apps add pages, agents, skills and schedules to Kiro Crew. See what ships with it, then build your own.
    pages: [apps/what-apps-are, apps/built-in-apps, apps/build-your-own-app]
---

# Kiro Crew Cookbook

A hands-on guide to running Kiro Crew for real work. Not reference docs — recipes.

Each recipe is one shape: **problem → steps → verify → gotchas.** You can read one and do the thing. You do not need to read them in order.

## Pick your path

- **New to Kiro:** [Install Kiro Crew step by step](./start/install.md), then [Your first hour](./start/first-hour.md).
- **I use Kiro CLI or IDE:** [Bring your Kiro setup](./start/bring-your-kiro-setup.md).
- **Kiro Crew is running:** [Security](./concepts/security.md), [Crewmates](./concepts/crewmates.md), [the knowledge library](./concepts/knowledge-base.md).

## Get started

1. **[Install Kiro Crew step by step](./start/install.md)** — every prerequisite, the installer, the gateway, keeping it running.
2. **[Your first hour](./start/first-hour.md)** — install, open the dashboard, get one useful task done.
3. **[Bring your Kiro setup](./start/bring-your-kiro-setup.md)** — steering, agents, skills, MCP servers and hooks from Kiro CLI or IDE.

## Concepts

- **[What Kiro Crew actually is](./concepts/what-kirocrew-is.md)** — the mental model. Gateway, session, agent, memory, in one picture.
- **[How Kiro Crew keeps you safe](./concepts/security.md)** — the checks every tool call passes before it runs.
- **[Crewmates](./concepts/crewmates.md)** — agents with their own memory, workspace and job.
- **[The knowledge library](./concepts/knowledge-base.md)** — let the agent search your docs and cite them.

## Recipes

1. **[Make it remember](./recipes/make-it-remember.md)** — memory and lessons, done right. What to teach it, what to keep out.
2. **[Teach it a skill](./recipes/teach-it-a-skill.md)** — a project-local skill, from a real case.
3. **[Schedule real work](./recipes/schedule-real-work.md)** — a cron job you would actually keep.
4. **[When it goes wrong](./recipes/when-it-goes-wrong.md)** — loops, blocked tools, drift, recovery.

## Who this is for

Engineers who are new to Kiro Crew. If you already use Kiro CLI or Kiro IDE, the guide skips "what is an agent" and gets to the parts that trip people up. If you have never used a Kiro product, start with the install page: it assumes nothing.

---

*Built from the Kiro Crew source, not from memory. Where Kiro Crew behaves differently across versions, the page says so.*
