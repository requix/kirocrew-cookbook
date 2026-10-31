---
title: How the pieces fit
description: "Sessions, agents, projects, steering, skills, tools, memory, mates, schedules and apps on one diagram. Experimental."
category: Concepts
difficulty: beginner
time: 8 min
surfaces: [dashboard, cli, channels]
tags: [concepts, mental-model, session, agent, memory, experimental]
updated: 2026-10-31
featured: true
layout: wide
---

KiroCrew has about a dozen words that matter, and the dashboard spreads them over many pages. This page puts them on one diagram, which adds each piece as you read the numbered steps.

```find-your-way
```

```concept-map
```

### 1. You talk to one gateway

KiroCrew is one process on your machine: the gateway. The dashboard, the `kirocrew` CLI and chat apps such as Slack or Teams are different doors into the same gateway, and everything else on this diagram lives inside it.

In the dashboard: the green dot in the top bar means you are connected. See [the dashboard map](../find/dashboard-map.md#zone=x.status).

### 2. Every chat is a session

A session is one conversation with its own history. A dashboard chat is a session, and so is a Slack thread or one run of a scheduled job. Many sessions run at the same time without seeing each other's conversation.

In the dashboard: **Sessions**, the first page in the sidebar. See [the dashboard map](../find/dashboard-map.md#zone=page.chat).

### 3. A session runs an agent

An agent is a config: its prompt, its tools and its MCP servers. The default agent is `kirocrew`, which is just another config, and each chat can run a different one.

In the dashboard: the agent name under the message box switches it, and **Customize → Custom agents** edits them. See [where it is](../find/where-is.md#task=switch-agent).

### 4. It works in a project folder

Each chat has a project folder, its working directory. The agent reads and writes files there, and that folder's own `.kiro/steering` files load for the chat.

In the dashboard: the folder name under the message box. See [where it is](../find/where-is.md#task=working-directory).

### 5. Steering and skills shape what it does

Steering files are standing rules: the global ones in `~/.kiro/steering` reach every session, and a project's own reach chats in that project. Skills are written procedures the agent loads only when a task needs one. Until then, it holds only each skill's name and description.

In the dashboard: **Customize → Steering** and **Customize → Skills**. Read [Teach it a skill](../recipes/teach-it-a-skill.md) and [Bring your Kiro setup](../start/bring-your-kiro-setup.md).

### 6. Tools do the work, through one gate

The agent acts through tools: the shell, files, search, and the tools of any MCP server you connect. Every tool call passes KiroCrew's gate first. Depending on the approval mode and your rules, the gate lets it run, asks you, or blocks it, and the agent cannot switch the gate off.

In the dashboard: the **Normal** button in the message box sets the approval mode, and **Customize → Connections** holds MCP servers. Read [How KiroCrew keeps you safe](security.md).

### 7. Memory carries over; the library is looked up

Memory is the small set of facts, preferences and lessons that comes back in later sessions, so a correction you make today still holds next week. The knowledge library is a different thing: your own documents, which the agent searches only when a question needs them.

In the dashboard: **Customize → Knowledge** for the library. Read [Make it remember](../recipes/make-it-remember.md) and [The knowledge library](knowledge-base.md).

### 8. A mate is an agent with its own memory

A mate, or crewmate, is a named assistant built from an agent config, with a memory store of its own. What it learns stays with it, so your on-call notes do not leak into a side project. Plain sessions share one global memory; each mate keeps its own.

In the dashboard: **Customize → Mates** lists your mates and makes new ones. To chat with a mate, open the **Mates** page in the sidebar; it shows only after you turn on **Settings → Developer → Mates**. See [where it is](../find/where-is.md#task=mates-page), and read [Crewmates](crewmates.md).

### 9. Schedules and apps start and extend it

A schedule starts a session on a timer, with an agent and a message, so work runs while you are away. An app adds pieces of every kind at once: agents, skills, MCP tools, schedules and dashboard pages, all behind one switch.

In the dashboard: **Schedule** in the sidebar, and **Discover** and **Library** under **Apps**. Read [Schedule real work](../recipes/schedule-real-work.md) and [What KiroCrew apps are](../apps/what-apps-are.md).

## The whole picture in one sentence

A session runs an agent in a project folder, shaped by steering and skills, acting through tools behind one gate, with memory that carries over. Mates, schedules and apps are ways to split that work, start it on a timer, and extend it.

## Where to go next

The layer under all of this, the gateway, the harness and the model, is explained in [What KiroCrew actually is](what-kirocrew-is.md).
