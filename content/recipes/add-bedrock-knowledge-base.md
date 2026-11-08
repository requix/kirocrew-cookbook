---
title: Add a Bedrock knowledge base
description: Connect an existing Amazon Bedrock Knowledge Base so knowledge search queries it live.
category: Knowledge
difficulty: intermediate
time: 15 min
surfaces: [dashboard]
tags: [knowledge, bedrock, aws]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew 0.12.0 or later running (see Your first hour)
  - An existing Amazon Bedrock Knowledge Base in your AWS account
  - You are the gateway owner
---

**Problem.** Your team already keeps documents in an Amazon Bedrock Knowledge Base, and the agent cannot see them. Copying them into Kiro Crew's own library would create a second copy that goes stale. Since 0.12.0 you can register the existing knowledge base instead and leave the data where it is.

Kiro Crew does not import anything. It queries the knowledge base live on each search and merges those results into the normal knowledge search.

## Before you start

Three things decide whether this works, so check them first.

- Only the gateway owner can add a Bedrock knowledge base. If you are not the owner, the option will not do anything for you.
- The knowledge base must already exist. This recipe registers it, it does not create one.
- The optional `bedrock` extra must be installed on the gateway host. Without it, the live queries have nothing to call AWS with.

Each search that reaches the knowledge base is billed by AWS, because every query is a real Bedrock call. A chatty agent that searches often will show up on your bill.

## Steps

### 1. Install the bedrock extra

Install the optional `bedrock` extra of Kiro Crew on the machine that runs the gateway, then restart the gateway. Use whichever install method you used originally, and add the extra to it.

### 2. Open the Sources page

In the dashboard, go to Capabilities, then Knowledge, then Sources.

### 3. Add the knowledge base

Choose Add Knowledge Base and fill in the details of your existing Bedrock Knowledge Base. Save it. It now appears in the list of sources next to your other knowledge.

### 4. Ask something it should know

Open a chat and ask about something that lives only in the Bedrock knowledge base:

```prompt
Search the knowledge base for our incident escalation policy and summarize it.
```

## Verify

- The new source shows up under Sources.
- The answer contains content you can trace back to a document in the Bedrock knowledge base.
- Your AWS bill or Bedrock usage metrics show the query. That confirms the search went out live.

## What can go wrong

**Problem:** There is no Add Knowledge Base option, or saving fails.

**Fix:** Check that you are signed in as the gateway owner. Other users cannot add one.

**Problem:** The source saves but searches return nothing from it.

**Fix:** Confirm the `bedrock` extra is installed on the gateway host and that the gateway was restarted afterwards. Then confirm the knowledge base itself returns results in the AWS console.

**Problem:** AWS costs go up after you connect it.

**Fix:** Searches are billed per query. Remove the source from Sources if you no longer want the agent calling it.

## What you learned

You registered an existing Bedrock Knowledge Base as a live source. Nothing was copied, results merge into knowledge search, and every search costs a Bedrock call.
