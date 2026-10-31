---
title: Build your own KiroCrew app
description: Build a standup app in three levels (agent and skill, dashboard page, weekday cron) and check each one works.
category: Apps
difficulty: advanced
time: 60 min
surfaces: [dashboard, cli]
tags: [apps, app-kit, scaffold, agent, cron, vite]
updated: 2026-10-30
featured: true
prerequisites:
  - KiroCrew running, gateway up
  - git, and a repository with a few recent commits
  - Node.js 22.12 or newer, for Level 2 only
---

You can already give KiroCrew an agent, a skill and a schedule by hand: drop a JSON file in `~/.kiro/agents`, write a `SKILL.md`, add a cron. An app puts all of that in one folder with an `app.json` manifest, so it installs, gets trusted, turns on and turns off as one unit. You can also share that folder. The concept is in [what apps are](./what-apps-are.md). This page builds one.

The example is `standup-notes`. It writes your daily standup from a project's git history. You build it in three levels, and each level works on its own:

| Level | Adds | Needs Node |
|---|---|---|
| 1 | An agent and a skill | No |
| 2 | A dashboard page with one button | Yes, 22.12+ |
| 3 | A cron that runs on weekday mornings | No |

The files below start from what `kirocrew app init` writes in KiroCrew 0.11.0, edited for the task. The manifest checks were run against that release's own validator.

## Level 1: agent and skill

This level has no page and no backend. It is an agent that runs `git log` and a skill that holds the standup format.

### 1. Scaffold the app

```bash
kirocrew app init standup-notes --dir ~/apps
```

`--dir` is the parent folder, and it is created if missing. The command prints the path it made and the install command to run later. You get this tree:

```tree
~/apps/standup-notes/
  app.json
  README.md
  assets/
    icon.png  # 512×512 placeholder, replace it before you publish
  agents/
    sample-agent.json
  skills/
    sample-skill/
      SKILL.md
```

Check: `cat ~/apps/standup-notes/app.json` shows `"displayName": "Standup Notes"` and your user name as `author`.

### 2. Rename the sample files

```bash
cd ~/apps/standup-notes
mv agents/sample-agent.json agents/standup-writer.json
mv skills/sample-skill skills/standup-format
```

### 3. Write the manifest

Replace `~/apps/standup-notes/app.json` with this:

```json
{
  "name": "standup-notes",
  "version": "0.1.0",
  "displayName": "Standup Notes",
  "description": "Writes a daily standup from the git history of a project",
  "author": "yourname",
  "iconPath": "assets/icon.png",
  "agents": ["agents/standup-writer.json"],
  "skills": ["skills/standup-format"],
  "tags": ["standup", "git"]
}
```

`name` is the app's id. It must be kebab-case, it becomes a folder name, and a bad one is refused at install, not fixed for you. `agents` and `skills` are paths inside the app folder. Level 1 needs no `permissions` block: the agent runs git through its own tools, not through any app API.

### 4. Write the agent

Replace `agents/standup-writer.json`:

```json
{
  "name": "standup-writer",
  "description": "Writes a daily standup from the git history of a project",
  "model": "auto",
  "prompt": "You write a developer's daily standup from git history. Work in the git repository the user names. If they name none, use the current working directory. Run git log for the commits since the last working day (on a Monday, since Friday), for example: git -C <repo> log --since=yesterday --date=short --pretty='%h %ad %an %s'. Then write the standup exactly as the standup-format skill says. Use only what the log shows. Never invent work.",
  "tools": ["fs_read", "grep", "glob", "execute_bash", "@kirocrew-core/skill_search"],
  "resources": ["skill://~/.kiro/crew/skills/standup-notes/standup-format/SKILL.md"]
}
```

Three fields do the real work.

- `name` is how you call the agent. KiroCrew writes the file as `~/.kiro/agents/standup-notes--standup-writer.json`, but agents are found by the `name` inside the file. So the agent is `standup-writer`, not `standup-notes--standup-writer`.
- `tools` is what the agent can use. `git log` needs the shell, which is `execute_bash`. The scaffold ships `"tools": []`, and with that the agent cannot run anything. `@kirocrew-core/skill_search` mounts one tool from KiroCrew's own server; KiroCrew fills in that server's spec when it registers the agent. Nothing here is auto-approved, so each git call asks you first, as in any chat.
- `resources` maps the skill to the agent. A custom agent sees no skills unless they are mapped with a `skill://` entry. On enable, KiroCrew links each app skill to `~/.kiro/crew/skills/<app>/<skill>/`, and that path is the one to name here. It also makes a short link at `~/.kiro/crew/skills/<skill>/`, but that one can belong to whichever app registered last.

### 5. Write the skill

Replace `skills/standup-format/SKILL.md`. Keep the frontmatter shape the scaffold wrote:

```markdown
---
description: The exact shape of a daily standup for the Standup Notes app
always: false
---

# Standup format

Write three sections, in this order. Each is a short bullet list.

## Yesterday
- What landed, grouped by what moved. Not one line per commit.

## Today
- What the commits suggest comes next. Only what the history supports.

## Blockers
- Anything a commit message flags as stuck, or "None".

Keep the whole standup short enough to read aloud in under a minute.
```

The format lives in the skill so you can change it without touching the agent.

### 6. Install it

```bash
kirocrew app install ~/apps/standup-notes
```

Install copies the folder to `~/.kiro/crew/apps/standup-notes/`. From now on KiroCrew reads that copy, not `~/apps`. Do not replace these commands with `curl`: the app routes need dashboard or app login, and a bare request is refused.

Check: `kirocrew app list` shows `standup-notes` with status `disabled`.

### 7. Trust it and turn it on

KiroCrew will not enable an app that is not built in until you trust it. That holds even for this one, which ships no code at all. Try the CLI first, so you see the gate:

```bash
kirocrew app enable standup-notes
```

It refuses with `blocked by execution policy: third-party app execution is disabled; trust this app alone in Settings (agent.apps_trusted), or set agent.apps_allow_third_party=true ...`.

Now trust it. You have two ways:

- **This app only.** In the dashboard, open **Library**, find **Standup Notes** and turn it on. The refusal comes back as a consent dialog that names what the app gets. Confirming it trusts this one app and retries the enable.
- **Every third-party app.** Turn on **Trust every third-party app** in **Settings → Security → Third-party apps**. This covers every app you install from now on, so prefer the first way.

Risk: a trusted app's Python, backend and install scripts run inside the gateway process, with no sandbox. Trust only code you have read.

Check:

- `kirocrew app list` shows `standup-notes` as `enabled`.
- `ls ~/.kiro/agents/standup-notes--standup-writer.json` finds the registered agent.
- `ls -l ~/.kiro/crew/skills/standup-notes/` shows a `standup-format` link into the installed copy.

### 8. Talk to the agent

In the dashboard, start a new chat whose project folder is your repository. Pick **standup-writer** in the agent selector in the chat's top bar or welcome screen, or type this in the chat:

```text
/agent standup-writer
```

Then ask:

```prompt
Write my standup
```

From a terminal, run it inside the repository, because the agent uses the working directory when you name no repo:

```bash
cd ~/work/my-repo
kirocrew chat --agent standup-writer -m "Write my standup"
```

The agent asks before it runs `git log`. Approve it.

Check: the reply has the three sections from the skill, and the transcript shows the `git log` call. If the sections are missing or in a different shape, the skill did not load: check the `resources` path against the link from step 7.

## Level 2: a dashboard page

This level adds a page with one button. The button opens a chat with `standup-writer` and puts a draft message in the box. The page is a React component, built into one ESM file that the dashboard loads.

### 1. Check Node

```bash
node --version
```

The app kit asks for Node 22.12 or newer (24 LTS is fine). Only this level needs it.

### 2. Add the UI files

`kirocrew app init --ui` writes the UI build files with the right settings. Do not run it on `~/apps`: it would overwrite your `app.json` and put the sample agent and skill back. Scaffold a second copy somewhere else and take its `ui/` folder:

```bash
kirocrew app init standup-notes --ui --dir /tmp/standup-ui
cp -r /tmp/standup-ui/standup-notes/ui ~/apps/standup-notes/ui
rm -rf /tmp/standup-ui
```

The file that matters is `ui/vite.config.ts`. It builds one ES module and marks the host's modules as external, so they are not bundled:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: 'src/App.tsx',
      formats: ['es'],
      fileName: () => 'index.mjs',
    },
    outDir: 'dist',
    rollupOptions: {
      external: [
        'react', 'react-dom', 'react/jsx-runtime',
        '@kirocrew/app-sdk', '@kirocrew/app-sdk/ui', 'lucide-react',
      ],
    },
  },
})
```

The dashboard provides React, ReactDOM, `@kirocrew/app-sdk` and `lucide-react` at runtime through its import map. That is how your page shares the dashboard's React, which hooks need. Do not `npm install` the SDK, and do not bundle any of these.

### 3. Write the page

Replace `ui/src/App.tsx`:

```tsx
import { useChatLauncher } from '@kirocrew/app-sdk'
import { Btn, Card, CardTitle, PageHeader } from '@kirocrew/app-sdk/ui'

export default function StandupNotes() {
  const { openChat } = useChatLauncher()

  return (
    <>
      <PageHeader title="Standup Notes" subtitle="A standup from your git history" />
      <div className="px-6 pb-8 overflow-y-auto flex-1 min-h-0">
        <Card>
          <CardTitle>Daily standup</CardTitle>
          <p className="text-sm text-muted">
            Opens a new chat with the standup writer. The message waits for you to send it.
          </p>
          <div className="mt-4">
            <Btn
              primary
              onClick={() =>
                openChat({
                  agent: 'standup-writer',
                  message: 'Write my standup for the repository at ~/work/my-repo',
                  autoSend: false,
                })
              }
            >
              Draft today's standup
            </Btn>
          </div>
        </Card>
      </div>
    </>
  )
}
```

`openChat` starts a new session when you pass no `slotKey`. `agent` only applies to a new session. `autoSend: false` leaves the message as a draft that you send yourself. Change the repository path to yours.

### 4. Add the page to the manifest

Add a `ui` block to `app.json`, beside the other keys:

```json
"ui": {
  "entry": "dist/index.mjs",
  "pages": [
    { "route": "/apps/standup-notes", "label": "Standup Notes", "icon": "Package" }
  ]
}
```

`entry` is relative to `ui/`. The page needs no `permissions` entry. `openChat` does not call a gateway API: it leaves a launch request for the chat page and moves you there. You only declare `permissions.api` and `permissions.events` when the page calls an API path or listens for an event; the SDK throws on any you did not declare. `icon` only works for built-in apps; an installed app's sidebar row shows a generic icon.

### 5. Build

```bash
cd ~/apps/standup-notes/ui
npm install
npm run build
```

Check: `ls ~/apps/standup-notes/ui/dist/index.mjs` finds the bundle.

### 6. Install the new version

KiroCrew runs the installed copy, so it does not see your edits yet. `kirocrew app install` refuses an app that is already installed, so uninstall and install again:

```bash
kirocrew app uninstall standup-notes
kirocrew app install ~/apps/standup-notes
```

Uninstall keeps the app's `data/` folder, but it also removes the trust grant. So turn the app on again from **Library** and confirm the consent dialog, as in Level 1 step 7.

Check:

- The sidebar shows **Standup Notes**, and the page shows the card and button.
- **Draft today's standup** opens a new chat on `standup-writer`, with the message in the box and not sent.

## Level 3: a cron on weekday mornings

This level runs the standup at 08:30 every weekday and posts the result to your notifications.

### 1. Add the cron

Add `crons` and `permissions` to `app.json`. The whole file now looks like this (drop the `ui` block if you skipped Level 2):

```json
{
  "name": "standup-notes",
  "version": "0.1.0",
  "displayName": "Standup Notes",
  "description": "Writes a daily standup from the git history of a project",
  "author": "yourname",
  "iconPath": "assets/icon.png",
  "agents": ["agents/standup-writer.json"],
  "skills": ["skills/standup-format"],
  "tags": ["standup", "git"],
  "ui": {
    "entry": "dist/index.mjs",
    "pages": [
      { "route": "/apps/standup-notes", "label": "Standup Notes", "icon": "Package" }
    ]
  },
  "crons": [
    {
      "name": "weekday-standup",
      "cron_expr": "30 8 * * 1-5",
      "timezone": "Europe/Berlin",
      "strict_schedule": true,
      "agent": "standup-writer",
      "message": "Write today's standup for the git repository at /home/you/work/my-repo.",
      "persistent_session": false
    }
  ],
  "permissions": {
    "cron": true
  }
}
```

What each cron field does:

| Field | Why it is there |
|---|---|
| `cron_expr` | `30 8 * * 1-5` is 08:30, Monday to Friday |
| `timezone` | Without it, the time is read in the gateway's configured zone, then UTC. Use your own IANA zone |
| `strict_schedule` | A daily job otherwise starts after a random delay of up to 59 minutes |
| `agent` | The declared agent name, as everywhere else |
| `message` | Names the repository by full path. A scheduled run has no project folder to fall back on |
| `persistent_session` | `false` gives each run a fresh session |

`silent` is left at its default, `false`, so each run's result is delivered to your notifications. `permissions.cron: true` is required. Without it, install fails with `crons is declared but permissions.cron is not: add "cron": true under "permissions" in app.json`.

### 2. Install the new version

```bash
kirocrew app uninstall standup-notes
kirocrew app install ~/apps/standup-notes
```

Turn it on again from **Library** and confirm the consent dialog. The cron is registered when the app is enabled.

### 3. Run it once now

You do not have to wait for 08:30. App crons get the app's name in front, so the job is `standup-notes/weekday-standup`. Find its id and fire it:

```bash
kirocrew cron list
kirocrew cron trigger <job-id>
```

The run asks before it runs `git log`, like your chat did. A manifest cron cannot set an approval mode, so the job uses the default, and a call nobody approves waits. Approve it when it asks.

If you want the 08:30 run to need nobody, change the job itself:

```bash
kirocrew cron update <job-id> --approval-mode auto
```

Risk: `auto` approves every tool call in that job, not just `git log`. The manifest does not own this setting, so an app update keeps it. A disable, enable or reinstall deletes and recreates the job, and then you set it again.

Check:

- The **Schedule** page lists `standup-notes/weekday-standup` with its next run in your zone.
- After the triggered run, your notifications show a standup with the three sections.

## When you need a backend

Levels 1 to 3 need no backend. Add one when the page must keep its own state, serve data the agent cannot fetch when asked, or call an outside API from server code instead of the browser.

```bash
kirocrew app init standup-notes --backend --dir /tmp/standup-backend
```

That writes `backend/server.py`, a small standard-library HTTP server, and adds a `backend` block to the manifest with `"entryPoint": "backend/server.py"`, `"port": "auto"` and `"healthCheck": "/health"`. The page reaches it through the gateway at `/apps/standup-notes/api/*`, on the same origin, so there is no CORS setup. The gateway signs every request it forwards. Check that signature in the backend before you trust a request:

```python
from kiro_crew.apps.proxy_auth import verify_proxy_request

ok = verify_proxy_request(
    header_value,        # the X-KiroCrew-Proxy request header
    method=method,       # "GET", "POST", ...
    target=self.path,    # the request target the backend received
    body=body_bytes,
)
```

It fails closed: no secret, a missing or malformed header, a timestamp more than 60 seconds off, or a wrong signature all return `False`. The secret reaches the backend in the `KIROCREW_PROXY_SECRET` environment variable. The health check is called unsigned, so leave `/health` open. A backend is executable code, so it only starts for a trusted app. For simple key-value state, `"storage": true` gives the app storage under `~/.kiro/crew/apps/standup-notes/data/`.

## Iterate

Changes to `app.json`, the agent or the skill reach KiroCrew through a new install, as in Level 2 step 6.

For UI work, dev mode saves the reinstall. It serves the page with caching off, watches the installed `ui/` folder, and reloads the page when a file changes. Point the installed `ui/` at your source folder with one link for the whole folder. A link to a single file answers `404`.

```bash
mv ~/.kiro/crew/apps/standup-notes/ui ~/.kiro/crew/apps/standup-notes/ui.installed
ln -s ~/apps/standup-notes/ui ~/.kiro/crew/apps/standup-notes/ui
kirocrew app dev standup-notes --confirm-out-of-install-root
```

The flag is needed because the folder now lives outside the install. It records a grant for that exact path, so if you move the link, run the command again. Then edit `ui/src/App.tsx` and run `npm run build`; the page reloads by itself. Turn dev mode off with `kirocrew app dev standup-notes --off`. Built-in apps cannot use dev mode.

## Publish it

So far the app installs from a path on your machine. Publishing puts it in a registry, so other people install it from **Discover**. The store card, icon and screenshots are read from your repository at a pinned commit, so `iconPath` must point at a real file in the repo. Commit the built `ui/dist/` folder: installs skip `node_modules`, `.git` and `.venv`. The full steps, store metadata and review rules are in the KiroCrew repository under `docs/app-kit/publishing-guide.md`.

## Verify

- `kirocrew app list` shows `standup-notes` enabled.
- `kirocrew app info standup-notes` prints the manifest you wrote.
- `~/.kiro/agents/standup-notes--standup-writer.json` exists.
- `~/.kiro/crew/skills/standup-notes/standup-format` links into the installed copy.
- `kirocrew chat --agent standup-writer -m "Write my standup"` in a repository returns the three sections.
- Level 2: the sidebar shows **Standup Notes**, and its button opens a drafted chat.
- Level 3: the **Schedule** page lists `standup-notes/weekday-standup`, and a triggered run lands in your notifications.

## Gotchas

- **The agent name is not the file name.** The file is `standup-notes--standup-writer.json`. You call `standup-writer`.
- **`kirocrew app init` overwrites.** Run on an existing app folder, it rewrites `app.json` and adds the sample files back.
- **The scaffold's agent has no tools.** `"tools": []` mounts nothing. Add `execute_bash` or the agent cannot run git.
- **A custom agent sees no skills unless you map them.** Name the namespaced path in `resources`.
- **Enable checks trust first.** An untrusted app is refused with `blocked by execution policy`, even one with no code.
- **Install refuses an installed app.** It says `already installed` and asks you to uninstall first or update.
- **Uninstall drops the trust grant.** Your data stays, but you confirm trust again on the next enable.
- **A scheduled run has no project folder.** Name the repository by full path in the cron `message`.
- **A manifest cron cannot set its approval mode.** Each tool call waits for you unless you set the job to `auto` yourself.
- **A daily cron starts late without `strict_schedule`.** The random delay can reach 59 minutes.
- **A cron time without `timezone` is not your local time.** It is the gateway's zone, then UTC.
- **A UI build is not live until you reinstall** or use dev mode.
- **Do not bundle React or the SDK.** A second React copy breaks hooks.

## Undo

Turn the app off. The agent, skill links, page and cron all go away, and the data stays:

```bash
kirocrew app disable standup-notes
```

Remove it. Its `data/` folder is kept, and the trust grant is removed:

```bash
kirocrew app uninstall standup-notes
```

To delete the data as well, add `--purge-data`. That cannot be undone:

```bash
kirocrew app uninstall standup-notes --purge-data
```

## Related

- [What apps are](./what-apps-are.md): the parts, the trust gate and the permission model.
- [Built-in apps](./built-in-apps.md): the 24 apps KiroCrew ships, to read as examples.
- [Teach it a skill](../recipes/teach-it-a-skill.md): skills without an app.
- [Schedule real work](../recipes/schedule-real-work.md): crons without an app.
- [How KiroCrew keeps you safe](../concepts/security.md): where the trust gate sits.
