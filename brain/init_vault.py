"""Vault initialization and conversion."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from importlib import resources
from pathlib import Path

from brain.app_config import default_app_config, write_default_app_config
from brain.vault import ensure_directories, resolve_vault_paths, write_text_file


@dataclass(slots=True)
class InitVaultResult:
    vault_path: Path
    created_paths: list[Path] = field(default_factory=list)
    reused_paths: list[Path] = field(default_factory=list)
    created_files: list[Path] = field(default_factory=list)
    reused_files: list[Path] = field(default_factory=list)
    folder_mappings: dict[str, str] = field(default_factory=dict)


def detect_folder_mappings(vault_path: Path) -> dict[str, str]:
    existing_dirs = {path.name.lower(): path.name for path in vault_path.iterdir() if path.is_dir()} if vault_path.exists() else {}
    defaults = {
        "daily_folder": "daily",
        "core_folder": "core",
        "references_folder": "references",
        "thoughts_folder": "thoughts",
        "system_folder": "system",
    }
    aliases = {
        "daily_folder": ["daily", "Daily"],
        "core_folder": ["core", "Core"],
        "references_folder": ["references", "References"],
        "thoughts_folder": ["thoughts", "Thoughts"],
        "system_folder": ["system", "System"],
    }

    mappings: dict[str, str] = {}
    for key, default_name in defaults.items():
        mappings[key] = default_name
        for alias in aliases[key]:
            if alias.lower() in existing_dirs:
                mappings[key] = existing_dirs[alias.lower()]
                break
    return mappings


def initialize_vault(
    vault_path: Path,
    *,
    agent: str,
    force_create_daily: bool = False,
    overwrite_system_files: bool = False,
) -> InitVaultResult:
    result = InitVaultResult(vault_path=vault_path)
    vault_path.mkdir(parents=True, exist_ok=True)
    folder_mappings = detect_folder_mappings(vault_path)
    result.folder_mappings = folder_mappings

    app_cfg = default_app_config(vault_path, agent)
    app_cfg.vault.daily_folder = folder_mappings["daily_folder"]
    app_cfg.vault.core_folder = folder_mappings["core_folder"]
    app_cfg.vault.references_folder = folder_mappings["references_folder"]
    app_cfg.vault.thoughts_folder = folder_mappings["thoughts_folder"]
    app_cfg.vault.system_folder = folder_mappings["system_folder"]

    vault_paths = resolve_vault_paths(app_cfg)
    created_dirs = ensure_directories(vault_paths)
    result.created_paths.extend(created_dirs)

    for path in [vault_paths.root, vault_paths.daily, vault_paths.core, vault_paths.references, vault_paths.thoughts, vault_paths.system]:
        if path not in created_dirs:
            result.reused_paths.append(path)

    claude_template = _template_text("CLAUDE.md")
    claude_path = vault_paths.system / "CLAUDE.md"
    if claude_path.exists() and not overwrite_system_files:
        result.reused_files.append(claude_path)
    else:
        write_text_file(claude_path, claude_template, overwrite=True)
        result.created_files.append(claude_path)

    config_path = vault_paths.system / "brain.config.yaml"
    config_already_exists = config_path.exists()
    write_default_app_config(
        config_path,
        vault_path,
        agent=agent,
        folder_overrides=folder_mappings,
        overwrite=overwrite_system_files,
    )
    if config_already_exists and not overwrite_system_files:
        result.reused_files.append(config_path)
    else:
        result.created_files.append(config_path)

    if force_create_daily:
        daily_path = vault_paths.daily / f"{date.today().isoformat()}.md"
        if daily_path.exists():
            result.reused_files.append(daily_path)
        else:
            content = _template_text("daily_note.md").replace("{{date}}", date.today().isoformat())
            write_text_file(daily_path, content, overwrite=False)
            result.created_files.append(daily_path)

    return result


def _template_text(name: str) -> str:
    return resources.files("brain.templates").joinpath(name).read_text(encoding="utf-8")
