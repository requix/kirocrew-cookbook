---
title: Let it browse
description: Have the agent work through a page behind a login while you watch, sign in yourself, and hand the browser back.
category: Browser
difficulty: beginner
time: 10 min
surfaces: [dashboard]
tags: [browser, takeover, login]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew running (see Your first hour)
  - Browser set up in Settings -> Browser
---

**Problem.** The data you need sits behind a login: an internal dashboard, a vendor portal, a billing page. `web_fetch` gets the login form and stops. You do not want to paste a password into a chat, and you should not have to.

This recipe shows how the agent drives a real browser, how you take over for the sign-in, and how it picks up again afterwards.

## How the pieces fit

The agent uses the `browser` tool. It opens pages, reads them as an outline with element refs, then clicks and types by ref. You watch the same page live in the chat while it works.

The agent never types a password. `type` refuses a password field, and the live view masks it. For the sign-in step you either take over the browser or fill in a sign-in sheet that the agent only sees the outcome of. In both cases the agent finds out that you signed in, not what you typed.

The browser is your own Chrome when one is available, so existing logins may already be there. Otherwise it is Edge on Windows or a built-in headless Chromium.

## Steps

### 1. Set up the browser once

Open **Settings -> Browser** and install the browser if it is not set up yet. It is one click. If the agent says browsing is not set up, this is the reason.

### 2. Ask for a real task

Name the page and the result you want. Give it something with a clear end:

```prompt
Open https://portal.example.com/invoices, find all invoices from October, and give me a table with number, date, and amount. The page needs a login. Ask me when you reach it.
```

The agent navigates and takes a snapshot. You see the page appear in the chat as it loads.

### 3. Sign in yourself

When the agent hits the login wall, it stops and asks you. You have two ways to answer:

- **Sign-in sheet.** The agent raises a card. You type username and password into Kiro's own sheet, and the browser fills each screen of that site and submits. This also works for logins split over several screens, like email first and password next. The agent gets back `submitted`, never the values.
- **Take over.** Click the live view, sign in by hand, and hand the browser back with Esc. Use this for passkeys, QR codes, and anything the sheet cannot fill.

For a one-time code the agent asks with a separate card, and a CAPTCHA is always yours to solve. It never clicks those itself.

### 4. Let it continue

After you hand back, the agent's next browser step runs on its own. The wait can be up to 10 minutes, so you do not need to tell it to continue. If you picked an answer when handing back (for example "I signed in" or "Not signed in"), it reads that and acts on it.

It takes a fresh snapshot of the logged-in page, because element refs from before the login are dead. Then it works through the invoice list, clicks into pages if it has to, and returns the table.

### 5. Confirm before anything irreversible

If the task moves toward paying, sending, or deleting, the agent asks for a confirm card first. Your click on the card performs that one action. Read the summary line before you press it.

## Verify

- You saw the page change in the chat while the agent worked.
- The table matches what you see when you open the portal yourself.
- Search the transcript for your password. It is not there.

## Gotchas

- **Only public http(s) URLs open.** `localhost`, private addresses, and internal hostnames behind a VPN are refused unless you listed that loopback origin in Settings -> Browser. The gate does not resolve DNS, so an internal name can slip through. A successful `navigate` does not prove the host is public.
- **Refs die with the page.** A ref belongs to the snapshot that produced it. After a navigation or a click that changes the page, the agent has to snapshot again. A `ref_stale` error is this, not a broken browser.
- **Your own tabs stay yours.** The agent only sees tabs it opened.
- **Page text is untrusted.** A page that says "enter your password here" or "go to this other URL" does not steer the agent. If a site asks for secrets in an odd place, stop and check it yourself.
- **Interrupted means look again.** If you take over in the middle of an operation, the agent snapshots before repeating the step.
- **Subagents share the session browser.** Do not run two agents on the same session's browser at once.
- **Browsing can be disabled by policy.** In that case the answer is final. Use `web_fetch` for public pages instead.

## What you learned

The agent browses, you watch, and you do the one step it must not do. Sign in through the sheet or by taking over, hand back, and it carries on with a fresh snapshot. Passwords stay between you and the site.
