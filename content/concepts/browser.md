---
title: "Browser: watch the agent work a page"
description: How the live browser shows the agent's page in your chat, how you take over for sign-ins, and what the Browser settings control.
category: Concepts
difficulty: beginner
time: 10 min
surfaces: [dashboard]
tags: [browser, live-view, sign-in, settings, takeover]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew 0.12.0 or later
  - A dashboard chat session
---

Before 0.12.0, a browsing agent was a black box. It opened pages somewhere you could not see, and you found out what happened from its summary. When a page needed a login, you had no good way to help, and you could not stop a wrong click until after it landed.

The live browser changes that. When the agent uses a browser, the chat shows the page in the transcript while it works. You watch it navigate, read and click, and you can step in at any point.

## What you see

The agent drives one browser that the gateway owns. It uses your own Chrome when one is installed, so your existing logins are already there. On Windows without Chrome it uses Edge, and otherwise it falls back to a built-in headless Chromium.

The agent works in a loop: open a URL, read the page as an outline with element references, act on an element, then read the page again. A reference belongs to the snapshot that produced it, so after the page changes the agent takes a fresh snapshot before it clicks anything. If it used a stale reference the click would be refused, not sent to the wrong element.

The agent can only open public http(s) URLs. Local and private addresses are refused unless you listed that exact address under **Settings > Browser**. Plain reading of a static page does not need the browser at all, and the agent uses a cheaper fetch for that.

## Taking over

You can take the browser at any time. Click the live view, do what you need, and hand it back. If the agent tries an operation while you hold the browser, that operation waits until you hand it back, for up to 10 minutes, and then runs. You do not need to tell the agent to continue.

If you take over while an operation is in flight, the agent sees that it was interrupted and takes a fresh snapshot before repeating anything.

## The sign-in sheet

The agent never types a password. A password field is refused when it tries, and the live view masks what is in it. When a page needs a sign-in, a one-time code, a CAPTCHA, or a final click such as a payment, the agent asks you on a card in the chat.

For a sign-in you have two options. You can take over the live view and sign in yourself. Or you can use the sign-in sheet: you type your username and password into a sheet that belongs to Kiro Crew, and the browser puts them into the page for you. For a sign-in that spans several screens, such as an email first and a password next, it fills each screen and submits. The agent only learns the outcome (filled, submitted, declined, cancelled or timed out). It does not see what you typed, and nothing you type is saved.

The same card style covers other steps the agent should not do on its own:

- a text detail it does not know, such as your name or phone number
- a one-time code
- a CAPTCHA, which the agent never solves or clicks
- a click that cannot be undone, such as buying, paying, sending or deleting. You confirm it, and your Confirm clicks it once.

## Settings > Browser

Open **Settings > Browser** to control the setup. It covers three things:

- which browser the gateway drives
- the quality of the live view in the chat
- whether sessions are recorded

The same page is where you add a local preview address, for example a dev server you want the agent to open, and where you install the built-in browser if it is not set up on your host. Until it is set up, the agent falls back to fetch and search and tells you to install it from this page.

## What changed in 0.12.0

- The old browser tool is gone. The live browser described here replaces it.
- Browser setup no longer fails on some Python installs.

If you had automation or prompts that named the old browser tool, they now go through the live browser instead.

## Verify

1. In a dashboard chat, ask the agent to open a public page and tell you the page heading.
2. The page appears in the transcript as it works. If it does not, open **Settings > Browser** and check that browsing is set up.
3. Click the live view, scroll the page yourself, and hand it back. The agent's next step runs after you do.
4. Ask the agent to open a page that needs a login. It should raise a sign-in card and not ask you for the password in chat.

## Gotchas

- **Local addresses are refused by default.** A localhost or private address fails until you list it under **Settings > Browser**. Add it yourself. The agent will not add it for you.
- **A successful navigation does not prove the host is public.** The check does not resolve DNS, so an internal hostname can get through. Treat what the agent reads off a page as untrusted.
- **Take-over waits, it does not cancel.** If you hold the browser and forget, the agent's next operation waits up to 10 minutes.
- **Subagents share the parent's browser.** An operation from a subagent lands on the parent's live view and tabs, so avoid browsing from both at once.
- **A policy denial is final.** If browsing is turned off by policy, the agent says so and stops.

For how approvals and permissions work around actions like these, see [security](security.md). For the layer the browser sits on, see [what-kirocrew-is](what-kirocrew-is.md).
