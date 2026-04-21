<p align="center">
  <img src="brain-logo.png" alt="brain²" width="96">
</p>

<h1 align="center">brain² (BrainSquared)</h1>

<p align="center">Your second brain, on your laptop. No cloud. No subscriptions. Just your data and an AI that knows it.</p>

<p align="center">
  <a href="https://pypi.org/project/brainsquared/"><img src="https://img.shields.io/pypi/v/brainsquared" alt="PyPI"></a>
  <img src="https://img.shields.io/pypi/pyversions/brainsquared" alt="Python">
  <img src="https://img.shields.io/github/license/Sushanti99/BrainSquared" alt="License">
</p>

---

brain² connects your tools — Gmail, Google Calendar, Notion, GitHub, Slack, Linear — and pulls them into a local Obsidian vault it manages for you. Every morning it generates a daily note with your tasks, events, and action items. You tick things off, chat with the AI, and your vault grows smarter over time. Everything runs on your machine.

---

## How it works

```
Browser UI  ──►  brain² Server  ──►  Claude Code / Codex CLI
                                              │
                                       Obsidian Vault (markdown)
                                              │
                             Gmail · Calendar · GitHub · Notion · Slack · Linear · RSS
```

- **Obsidian is the database.** No SQLite, no Redis — just markdown files you already own.
- **Daily note as your task hub.** Tasks, events, emails, and PRs pulled fresh each day. Tick things off — they don't come back tomorrow.
- **The agent is swappable.** Claude Code or Codex, configured at startup.
- **Karpathy-style vault updates.** When you connect a new tool, brain² surgically updates your existing notes rather than dumping raw data.
- **Everything is local.** Your vault, your machine, your data.

---

## Quickstart

### 1. Install

```bash
pip install brainsquared
```

Requires [Claude Code](https://claude.ai/code) (or Codex) installed and authenticated.

### 2. Seed a new vault

```bash
brain seed --vault ~/my-vault \
           --from-obsidian ~/path/to/existing-vault \
           --from-notion \
           --from-gmail \
           --from-calendar
```

brain² collects your existing data, runs it through Claude, and populates:

```
my-vault/
├── core/          ← profile, projects, interests, people
├── references/    ← reference material
├── daily/         ← today's note with tasks, events, emails
├── thoughts/      ← AI conversation summaries (auto-written)
└── system/        ← config and agent instructions
```

### 3. Start

```bash
brain start --vault ~/my-vault
```

Opens `http://localhost:3000`.

---

## The UI

brain² has a three-tab interface:

**Tasks** — Your daily note lives here. Tasks from all your connected tools appear as interactive checkboxes. Tick something off and it won't show up tomorrow. Anything left unticked carries forward automatically. Use the ⚙ settings button to choose which integrations appear in your daily note.

**Home** — Browse your vault and seed it from the UI. See which integrations are connected at a glance.

**Integrations** — Connect your tools without touching a config file. Paste an API key or go through OAuth — brain² stores credentials locally and starts pulling context immediately.

The panel between your daily note and the chat window is draggable. Your layout is remembered across sessions.

---

## Integrations

| Integration | Used for |
|---|---|
| Google Calendar | Daily note events |
| Gmail | Daily note action items |
| GitHub | Open PRs and assigned issues |
| Notion | Open tasks and pages |
| Slack | Recent channel messages |
| Linear | Issues via MCP |
| RSS feeds | Reading list in daily note |

All integrations are optional. brain² works with just a vault and Claude Code.

---

## All commands

```bash
brain seed    --vault PATH  [--from-obsidian PATH] [--from-notion] [--from-gmail] [--from-calendar] [--dry-run]
brain init    --vault PATH  [--agent claude-code|codex]
brain start   --vault PATH  [--agent claude-code|codex] [--port N] [--no-open]
brain daily   --vault PATH  [--force]
brain status  --vault PATH
```

---

## Vault structure

| Folder | Purpose |
|---|---|
| `core/` | Persistent notes: profile, projects, interests, people |
| `references/` | Reference material, links, resources |
| `daily/` | One note per day, generated from integrations |
| `thoughts/` | Auto-written summaries of AI conversations |
| `system/` | `brain.config.yaml` and agent instructions |

---

## Development

```bash
git clone https://github.com/Sushanti99/BrainSquared
cd BrainSquared
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
pytest -q
```

---

## Roadmap

- [ ] `brain setup` — guided OAuth so each user owns their own Google credentials
- [ ] Move integration clients into `brain/integrations/`
- [ ] VPS deployment with Obsidian remote sync
- [ ] Mobile access via Tailscale
- [ ] Background scheduled daily note generation
