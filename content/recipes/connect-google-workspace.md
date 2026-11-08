---
title: Connect Google Workspace
description: Create your own Google OAuth app and connect Gmail, Drive, Calendar, Sheets, Docs and Slides.
category: Connections
difficulty: intermediate
time: 30 min
surfaces: [dashboard]
tags: [connections, google, oauth]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew 0.12.0 or later
  - A Google account that can create a Google Cloud project
---

**Problem.** You want the agent to read your mail, find a file in Drive, or check your calendar. Google does not let Kiro Crew register itself as an app on the fly, so there is no one-click Connect for these services. You register your own OAuth app once, paste it into Kiro Crew, and all six Google cards use it.

## What you get

Release 0.12.0 adds six Google cards to **Customize → Connections**: Gmail, Google Drive, Google Calendar, Google Sheets, Google Docs and Google Slides. Each card reads "Configure OAuth app" until you finish this recipe.

One OAuth client serves all six cards. You create it once and paste the same client ID and secret into each.

## Steps

### 1. Open the OAuth Apps panel first

Go to **Settings → OAuth Apps**. It shows the exact redirect URI you have to register in Google. Copy it now, because Google rejects the sign-in if the string differs by even one character.

### 2. Create a Google Cloud project

1. Open the [Google Cloud console](https://console.cloud.google.com/) and create a new project. A dedicated project keeps the app easy to find and delete later.
2. Open **APIs & Services → Library** and enable the APIs for the services you plan to use: Gmail API, Google Drive API, Google Calendar API, Google Sheets API, Google Docs API and Google Slides API.

Enable only the ones you need. A card for a service whose API is off will sign in and then fail on the first call.

### 3. Configure the consent screen

1. Open **APIs & Services → OAuth consent screen**.
2. Pick **External** for a personal Google account, or **Internal** if you are on a Workspace domain and only your organization will use it.
3. Fill in the app name and your email address.
4. While the app is in **Testing** status, add your own Google account under **Test users**. Without that, Google blocks the sign-in.

In Testing status, Google also expires refresh tokens after about a week, so you sign in again regularly. Publishing the app avoids that, but for sensitive scopes such as Gmail, Google asks for a verification review. For a personal setup, Testing is the usual choice.

### 4. Create the OAuth client

1. Open **APIs & Services → Credentials** and choose **Create credentials → OAuth client ID**.
2. Set the application type to **Web application**.
3. Under **Authorized redirect URIs**, paste the URI you copied from **Settings → OAuth Apps**.
4. Create it and keep the client ID and client secret on screen.

### 5. Enter the client in Kiro Crew

Back in **Settings → OAuth Apps**, enter the client ID and the client secret for each Google entry. The client ID goes into `config.json` under `connections.oauth_clients.<slug>.client_id`. The secret goes into the encrypted vault as `CONNECTIONS_<SLUG>_CLIENT_SECRET`. The panel handles both, and it never reads the secret back, so a screenshot of it leaks nothing.

Do not write the secret into an MCP server entry by hand. It would sit in plaintext in a file the agent can read.

### 6. Connect each service

Open **Customize → Connections**, pick a Google card and start the sign-in. Google shows a consent screen listing the scopes. Approve it with the account you added as a test user.

Repeat for each service you want. After the sign-in, drain the warm pool or restart the gateway, then start a fresh session. A running session caches its tool list, so a new chat alone can come up without the new tools.

## What the agent can do

Each service exposes its own tools, so the exact list depends on the Google MCP endpoint behind the card. In practice, expect this:

| Service | Typical use |
|---|---|
| Gmail | Search and read messages, summarize a thread, draft a reply |
| Google Drive | Find files by name or content, read them, list a folder |
| Google Calendar | List upcoming events, check availability, create an event |
| Google Sheets | Read ranges, update cells, append rows |
| Google Docs | Read a document, edit or append text |
| Google Slides | Read a deck, add or edit slides |

To see what the agent has in your session, run the card's **Test** action. It starts a promptless session, reads the real tool inventory and reports **usable**, **no tools** or **failed**. It never calls a tool, so it cannot touch your account.

A first prompt to try:

```prompt
Find the three most recent emails from my manager and summarize them in two lines each.
```

## Verify

- The card's badge reads **Signed in** and the health badge reads `ok`.
- **Test** reports **usable**.
- In a new session, the prompt above returns real messages from your inbox.

## Gotchas

- **Redirect URI mismatch.** The most common failure. Copy the URI from **Settings → OAuth Apps** and paste it unchanged into the Google client.
- **Access blocked for a test user.** The Google account you sign in with has to be listed under **Test users** on the consent screen while the app is in Testing.
- **Sign-in worked but no data.** The API for that service is not enabled in your Google Cloud project, or you approved the consent screen with a different account.
- **Tools missing in chat.** Drain the warm pool or restart the gateway, then open a new session.
- **Removing a card's config does not revoke the grant.** Use the card's **Disconnect**, or the revoke page in your Google account permissions, when you want to end access.
- **Keep the scope small.** Gmail and Drive hold a lot of private data. Connect only the services you will use, and read the consent screen before approving.

## What you learned

Google Workspace needs your own OAuth app because Google does not allow runtime registration. Register one Web client with the redirect URI from **Settings → OAuth Apps**, enter it for each Google entry, sign in per service, and start a fresh session after the warm pool is drained.
