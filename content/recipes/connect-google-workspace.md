---
title: Connect Google Workspace
description: Create one Google OAuth app and connect Gmail, Drive, Calendar, Sheets, Docs and Slides with it.
category: Connections
difficulty: intermediate
time: 20 min, plus a few days' wait the first time
surfaces: [dashboard]
tags: [connections, google, oauth]
updated: 2026-11-19
featured: false
prerequisites:
  - Kiro Crew 0.13.0 or later
  - A Google account that can create a Google Cloud project
  - The gcloud CLI, for the setup script
---

**Problem.** You want the agent to read your mail, find a file in Drive, or check your calendar. Google does not let Kiro Crew register itself as an app on the fly, so there is no one-click Connect for these services. You register your own OAuth app once, paste it into Kiro Crew once, and all six Google products use it.

This is a private setup: your own Google account, your own Kiro Crew.

## What you get

**Settings → Connections** has one **Google** entry. Inside it are six products: Gmail, Google Drive, Google Calendar, Google Sheets, Google Docs and Google Slides. They share one Google OAuth client.

Before 0.13.0 these were six separate cards under **Customize → Connections**, each with its own copy of the client. If you set them up then, they keep working. You only need this recipe for a new setup or a new client.

## Steps

### 1. Run the setup script

Kiro Crew ships a script that does the Google Cloud part for you. Get it from the [Kiro Crew repository](https://github.com/kirodotdev/KiroCrew/tree/v0.13.0/scripts) (`google-oauth-setup.sh` for macOS and Linux, `google-oauth-setup.ps1` for Windows), then run it:

```bash
scripts/google-oauth-setup.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\google-oauth-setup.ps1
```

It signs you in to gcloud, picks or creates a project named **Kiro Crew**, enables the twelve APIs the six products need, and prints your **Project number**, a line of scopes, six redirect URIs and direct links for the next step. To use a project you already have, pass its ID: `scripts/google-oauth-setup.sh my-project`. Running it again is safe. It changes nothing already set and writes nothing to disk.

Keep the output on screen. You need it for the next step.

### 2. Three steps in Google's console

Google has no API for these, so you click them. The script's links open each page with your project already selected.

1. **Join the Developer Preview.** Google's MCP servers are a Developer Preview, and they refuse calls until Google accepts your project. Open [the Workspace preview page](https://developers.google.com/workspace/preview), click **Apply to join** and paste the Project number. Acceptance usually takes a few days. If the script said the MCP APIs did not enable yet, run it again after Google's email.
2. **Consent screen.** Open the **Branding** link and click **Get Started**. Name the app `Kiro Crew` and use your own email for support and contact.
   - **Audience:** pick **Internal** if it is offered (a Google Workspace account). Otherwise pick **External**, stay in **Testing**, and add yourself under **Audience → Test users**.
   - **Data Access → Add or Remove Scopes → Manually add scopes:** paste the scope line the script printed, then **Add to Table**, **Update**, **Save**.
3. **OAuth client.** Open the **Create client** link.
   - Set **Application type** to **Web application**.
   - Under **Authorized redirect URIs**, add the six URIs the script printed. You can add only the products you will use.
   - Tick **Use this client for an AI-powered agent**. Google's MCP servers reject a client without it.
   - Click **Create** and copy the **Client ID** and **Client secret**. Google shows the full secret only once.

### 3. Paste once

In Kiro Crew, open **Settings → Connections** and open the **Google** entry. Paste the Client ID and Client secret, leave **Also save on Google Drive, …** on, and click **Save**. All six products now show **Configured**.

The panel stores the secret in the encrypted vault and never shows it back. Do not write it into an MCP server entry by hand, where it would sit in plain text in a file the agent can read.

### 4. Connect each product

Still in the **Google** entry, click **Connect** on each product you want. Google shows a consent screen. Approve it with the account you added as a test user. On **External / Testing**, Google first warns "Google hasn't verified this app". Click **Continue**. That is expected for a private app.

Then start a fresh session. A running session keeps the tool list it started with.

## What the agent can do

Kiro Crew asks Google only for read-only scopes. The agent can search and read. It cannot send, edit or create.

| Product | What works | What fails |
|---|---|---|
| Gmail | Search threads, read messages, list labels and drafts | Creating drafts, labelling |
| Google Drive | Find and read files | Anything that writes |
| Google Calendar | List calendars and events, check free/busy | Creating or changing events |
| Google Sheets | Read spreadsheets | Editing cells |
| Google Docs | Read documents | Editing |
| Google Slides | Read decks | Editing |

A write tool may still show up in the agent's tool list, because Google's server lists it. A call to it fails with a permission error. Adding more scopes on Google's **Data Access** page does not change this, since Kiro Crew requests only the read-only ones.

A first prompt to try:

```prompt
Find the three most recent emails from my manager and summarize them in two lines each.
```

## Verify

- Every product you connected shows as connected in the **Google** entry.
- In a new session, the prompt above returns real messages from your inbox.

## Gotchas

- **`redirect_uri_mismatch`.** That product's URI is missing from the client or differs by a character. Use `127.0.0.1`, not `localhost`, and no trailing slash. Client edits can take a few minutes to apply.
- **`access_denied` or "app is being tested".** Your account is not under **Audience → Test users**.
- **`403` or "API has not been used in project".** Google has not accepted the project into the Developer Preview yet, or an MCP API is off. Run the script again.
- **Sign-in works, every tool call is rejected.** The client is missing **Use this client for an AI-powered agent**. You cannot add it to an existing client. Create a new one and paste it again.
- **Access ends after a week.** On **External / Testing**, Google expires the grant seven days after you consent. Click **Connect** again. **Internal** does not expire this way.
- **Remote or Docker install.** After consent the browser lands on `http://127.0.0.1:<port>/callback?...` and the page fails to load. Copy the whole URL from the address bar into the field Kiro Crew shows during Connect.
- **Changing only the Client ID saves on one product.** Enter the secret again to update all six.
- **Revoking.** Remove the app at [your Google account permissions](https://myaccount.google.com/permissions). That ends every Google product connected through it at once.
- **Mail is untrusted input.** An email can carry text written to steer the agent. Review what the agent does with what it reads.

## What you learned

Google needs your own OAuth app because it does not allow runtime registration. The script prepares the project, three console steps make the client, and one paste in **Settings → Connections** serves all six products. Connect each one, then start a fresh session.
