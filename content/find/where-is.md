---
title: "Where is it? The hard-to-find controls"
description: Pick a task, and a pointer walks the clicks to a hidden control in a drawn Kiro Crew dashboard. Experimental.
category: Find your way
difficulty: beginner
time: 5 min
surfaces: [dashboard]
tags: [navigation, dashboard, where-is, experimental]
updated: 2026-10-31
featured: true
layout: wide
---

A few Kiro Crew controls are hard to find, and this page covers only those. Pick a task, and a pointer clicks through a drawing of the dashboard. The numbered steps above the drawing say the same in words.

```find-your-way
```

```where-is
```

## Same thing, different name

Some Kiro Crew names differ from the words people search for. The search box above knows both, and this table lists the common ones.

| You may call it | Kiro Crew calls it | Where |
|---|---|---|
| Working directory, cwd | Project | The folder name under the message box |
| Crewmate, crew member | Mate | **Customize → Mates** |
| MCP servers | Connections | **Customize → Connections** |
| Agent config, agent JSON | Custom agents | **Customize → Custom agents** |
| Rules, instructions | Steering | **Customize → Steering** |
| Permissions, auto-approve | Approval mode | The **Normal** button in the message box |
| A long unattended job | Task Runner | Left sidebar, under **Apps** |
| Run history of a job | Executions | **Schedule** |

## Why things hide

Every task on this page is there for one of five reasons, shown as a tag on each answer.

| Reason | Example |
|---|---|
| Behind a menu | **Skill** and **Upload file** live in **Add files & options**, the **+** in the message box |
| Shows only sometimes | The memory mode button is there only before the first message of a chat |
| Needs a switch first | The **Mates** page appears only after **Settings → Developer → Mates** is on |
| Has another name | The working directory is called **Project** |
| Deep in Settings or Customize | Reply length is **Settings → Chat → Transcript → Response Verbosity** |

Things you can see on the first screen, like **New**, **Settings** or the search bar, are not on this page.

## Faster ways to get there

- **Search.** Press Cmd+K on a Mac or Ctrl+K elsewhere. It searches sessions, files and commands. With the **Command Bar** app on, which it is by default, the same keys open a launcher for commands, pages and settings.
- **Ask the agent.** In a dashboard chat, ask "where is the approval-mode picker?" or "how do I change the working directory?". The agent looks the control up in the same map this page uses, and it can point at it in your own tab. Each answer above has a question ready to copy.
- **Keys.** **Settings → Shortcuts** lists the keyboard shortcuts.

## Every answer in one table

The same answers without the animation. Each task name links to its animation above.

```where-is-table
```

## Where the labels and drawing come from

This page and [the dashboard map](dashboard-map.md) use the same sources. The labels and click paths come from Kiro Crew's own UI index. It is the file the agent reads to find controls, and it ships inside each Kiro Crew release. Both pages use the copy from Kiro Crew 0.11.0. A release can move or rename things, so the cookbook build checks every task and every map part against that copy and stops if a control is gone.

Two controls are not in the index yet: the project folder and the agent picker under the message box. Their paths come from the Kiro Crew docs instead. The drawing follows real Kiro Crew screenshots but leaves things out, so your screen shows more than it does.
