# brain

`brain` is a local-first personal agent harness on top of an Obsidian vault.

It can:
- initialize or convert a vault into Brain format
- start a local FastAPI server with a minimal browser chat UI
- run either Claude Code or Codex against the vault
- generate daily notes from Gmail, Google Calendar, Notion, and vault tasks
- end a session by writing only a markdown summary into `thoughts/`

The older flat scripts are still present as compatibility wrappers where needed, but the primary interface is now the installable `brain` CLI.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

## Onboarding Integrations

The old onboarding flow now lives in `bootstrap.py`:

```bash
python bootstrap.py
```

It writes local credentials into `.env`. Gmail, Calendar, Notion, and custom RSS feeds remain optional.

## Initialize A Vault

```bash
brain init --vault /absolute/path/to/vault --agent claude-code
```

This creates any missing Brain folders and writes:
- `system/brain.config.yaml`
- `system/CLAUDE.md`

Existing compatible folder names such as `Daily/` are preserved through config mapping instead of being renamed automatically.

## Start The App

```bash
brain start --vault /absolute/path/to/vault
```

This starts the local server and opens the browser UI by default. The UI supports:
- one active websocket session
- streaming responses
- `Generate Daily`
- `End & Summarize`

## Generate Today’s Daily Note

```bash
brain daily --vault /absolute/path/to/vault
```

By default, Brain refuses to overwrite today’s existing daily note.

Reading links are now opt-in. To include them in generated daily notes, set `integrations.include_reading_list_in_daily_note: true` in `system/brain.config.yaml`.

## Status

```bash
brain status --vault /absolute/path/to/vault
```

This reports:
- vault path
- configured agent
- backend binary path and version
- folder mapping
- integration readiness

## Compatibility

`main.py` now delegates to the new CLI:

```bash
python main.py daily --vault /absolute/path/to/vault
python main.py chat --vault /absolute/path/to/vault
```

`python main.py chat` is treated as `brain start`.

## Package Layout

```text
brain/
├── cli.py
├── app_config.py
├── env_config.py
├── init_vault.py
├── vault.py
├── prompts.py
├── agent_backends.py
├── session.py
├── summarizer.py
├── daily.py
├── integration_context.py
├── server.py
├── models.py
└── web/index.html
```

## Tests

```bash
.venv/bin/python -m pytest -q
```

## Notes

- `setup.py` is now a packaging shim for editable installs.
- `bootstrap.py` is the interactive integration setup script.
- Optional integrations fail independently so the core app can still run with only a vault and a local agent CLI.
