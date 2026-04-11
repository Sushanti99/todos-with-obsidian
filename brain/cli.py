"""Brain command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from brain import __version__
from brain.agent_backends import get_backend
from brain.app_config import load_app_config
from brain.env_config import integration_status, load_env_config
from brain.init_vault import initialize_vault


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="brain — local-first personal agent harness for an Obsidian vault")
    parser.add_argument("--version", action="version", version=f"brain {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize or convert a Brain-compatible vault")
    init_parser.add_argument("--vault", required=True, help="Vault path to create or convert")
    init_parser.add_argument("--agent", choices=["claude-code", "codex"], default="claude-code")
    init_parser.add_argument("--force-create-daily", action="store_true")
    init_parser.add_argument("--overwrite-system-files", action="store_true")
    init_parser.set_defaults(func=cmd_init)

    start_parser = subparsers.add_parser("start", help="Start the Brain local server")
    start_parser.add_argument("--vault", help="Vault path")
    start_parser.add_argument("--config", help="Explicit path to brain.config.yaml")
    start_parser.add_argument("--agent", choices=["claude-code", "codex"])
    start_parser.add_argument("--port", type=int)
    start_parser.add_argument("--no-open", action="store_true")
    start_parser.set_defaults(func=cmd_start)

    status_parser = subparsers.add_parser("status", help="Show vault, integration, and backend readiness")
    status_parser.add_argument("--vault", help="Vault path")
    status_parser.add_argument("--config", help="Explicit path to brain.config.yaml")
    status_parser.add_argument("--agent", choices=["claude-code", "codex"])
    status_parser.set_defaults(func=cmd_status)

    daily_parser = subparsers.add_parser("daily", help="Generate today's daily note")
    daily_parser.add_argument("--vault", help="Vault path")
    daily_parser.add_argument("--config", help="Explicit path to brain.config.yaml")
    daily_parser.add_argument("--force", action="store_true")
    daily_parser.set_defaults(func=cmd_daily)

    return parser


def cmd_init(args: argparse.Namespace) -> int:
    result = initialize_vault(
        Path(args.vault).expanduser().resolve(),
        agent=args.agent,
        force_create_daily=args.force_create_daily,
        overwrite_system_files=args.overwrite_system_files,
    )
    print(f"Vault: {result.vault_path}")
    print("Created directories:")
    for path in result.created_paths or []:
        print(f"  - {path}")
    if not result.created_paths:
        print("  - none")
    print("Reused directories:")
    for path in result.reused_paths or []:
        print(f"  - {path}")
    if not result.reused_paths:
        print("  - none")
    print("Created files:")
    for path in result.created_files or []:
        print(f"  - {path}")
    if not result.created_files:
        print("  - none")
    print("Reused files:")
    for path in result.reused_files or []:
        print(f"  - {path}")
    if not result.reused_files:
        print("  - none")
    print("Folder mapping:")
    for key, value in result.folder_mappings.items():
        print(f"  - {key}: {value}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    from brain.server import run_server

    app_cfg = load_app_config(
        vault_path=args.vault,
        config_path=args.config,
        agent_override=args.agent,
        port_override=args.port,
    )
    backend = get_backend(app_cfg)
    validation = backend.validate_installation()
    if not validation.installed:
        raise RuntimeError(validation.error or f"Backend unavailable: {app_cfg.agent}")
    env_cfg = load_env_config()
    run_server(app_cfg, env_cfg, open_browser=not args.no_open)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    app_cfg = load_app_config(
        vault_path=args.vault,
        config_path=args.config,
        agent_override=args.agent,
    )
    env_cfg = load_env_config()
    backend = get_backend(app_cfg)
    validation = backend.validate_installation()
    integrations = integration_status(env_cfg)

    print(f"Vault path: {app_cfg.vault.path}")
    print(f"Configured agent: {app_cfg.agent}")
    print(f"Agent binary path: {validation.resolved_path or 'missing'}")
    print(f"Agent version: {validation.version or 'unknown'}")
    print(f"Server port: {app_cfg.server.port}")
    print("Folder mapping:")
    print(f"  daily: {app_cfg.vault.daily_folder}")
    print(f"  core: {app_cfg.vault.core_folder}")
    print(f"  references: {app_cfg.vault.references_folder}")
    print(f"  thoughts: {app_cfg.vault.thoughts_folder}")
    print(f"  system: {app_cfg.vault.system_folder}")
    print("Integrations:")
    print(f"  Google credentials: {'present' if integrations['google'] else 'missing'}")
    print(f"  Notion: {'configured' if integrations['notion'] else 'missing'}")
    print(f"  News feeds: {'configured' if integrations['news'] else 'default-only'}")
    return 0


def cmd_daily(args: argparse.Namespace) -> int:
    from brain.daily import generate_daily_note

    app_cfg = load_app_config(vault_path=args.vault, config_path=args.config)
    env_cfg = load_env_config()
    path = generate_daily_note(app_cfg, env_cfg, force=args.force)
    print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
