"""Vault utilities and Obsidian note parsing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from brain.models import AppConfig, ObsidianNote, VaultPaths


def resolve_vault_paths(app_cfg: AppConfig) -> VaultPaths:
    root = app_cfg.vault.path
    return VaultPaths(
        root=root,
        daily=root / app_cfg.vault.daily_folder,
        core=root / app_cfg.vault.core_folder,
        references=root / app_cfg.vault.references_folder,
        thoughts=root / app_cfg.vault.thoughts_folder,
        system=root / app_cfg.vault.system_folder,
    )


def ensure_directories(vault_paths: VaultPaths) -> list[Path]:
    created: list[Path] = []
    for path in [vault_paths.root, vault_paths.daily, vault_paths.core, vault_paths.references, vault_paths.thoughts, vault_paths.system]:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)
    return created


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    yaml_block = text[4:end].strip()
    body = text[end + 4 :].lstrip("\n")
    metadata: dict[str, Any] = {}

    for line in yaml_block.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
    return metadata, body


def extract_tags(text: str, frontmatter: dict[str, Any]) -> list[str]:
    tags = set()
    for match in re.finditer(r"(?<!\S)#([a-zA-Z0-9_/-]+)", text):
        tags.add(match.group(1))
    raw_tags = frontmatter.get("tags", "")
    if isinstance(raw_tags, str):
        for item in re.split(r"[,\s]+", raw_tags):
            candidate = item.strip().lstrip("#")
            if candidate:
                tags.add(candidate)
    return sorted(tags)


def extract_links(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", text)


def extract_tasks(text: str) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"\s*-\s+\[([ xX])\]\s+(.*)", line)
        if match:
            tasks.append(
                {
                    "done": match.group(1).lower() == "x",
                    "text": match.group(2).strip(),
                    "line": line_number,
                }
            )
    return tasks


def read_note(path: Path, vault_root: Path) -> ObsidianNote:
    raw = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = parse_frontmatter(raw)
    folder = str(path.parent.relative_to(vault_root)) if path.parent != vault_root else ""
    return ObsidianNote(
        path=path,
        relative_path=str(path.relative_to(vault_root)),
        title=frontmatter.get("title") or path.stem,
        content=body,
        raw_content=raw,
        frontmatter=frontmatter,
        tags=extract_tags(body, frontmatter),
        links=extract_links(body),
        tasks=extract_tasks(body),
        folder=folder,
    )


def read_vault(root: Path) -> list[ObsidianNote]:
    notes: list[ObsidianNote] = []
    if not root.exists():
        return notes
    for markdown_file in sorted(root.rglob("*.md")):
        if ".obsidian" in markdown_file.parts:
            continue
        try:
            notes.append(read_note(markdown_file, root))
        except OSError:
            continue
    return notes


def read_daily_note(vault_paths: VaultPaths, day: str) -> str | None:
    note_path = vault_paths.daily / f"{day}.md"
    if not note_path.exists():
        return None
    return note_path.read_text(encoding="utf-8")


def list_core_notes(vault_paths: VaultPaths) -> list[ObsidianNote]:
    if not vault_paths.core.exists():
        return []
    return [read_note(path, vault_paths.root) for path in sorted(vault_paths.core.rglob("*.md"))]


def list_thought_summaries(vault_paths: VaultPaths) -> list[Path]:
    if not vault_paths.thoughts.exists():
        return []
    return sorted(vault_paths.thoughts.glob("*.md"))


def note_exists(path: Path) -> bool:
    return path.exists()


def write_text_file(path: Path, content: str, *, overwrite: bool = True) -> Path:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def detect_compatible_vault_structure(vault_root: Path) -> dict[str, str]:
    mappings: dict[str, str] = {}
    aliases = {
        "daily_folder": ["daily", "Daily"],
        "core_folder": ["core", "Core"],
        "references_folder": ["references", "References"],
        "thoughts_folder": ["thoughts", "Thoughts"],
        "system_folder": ["system", "System"],
    }
    existing_names = {path.name.lower(): path.name for path in vault_root.iterdir() if path.is_dir()} if vault_root.exists() else {}
    for key, names in aliases.items():
        for name in names:
            if name.lower() in existing_names:
                mappings[key] = existing_names[name.lower()]
                break
    return mappings


def snapshot_vault_mtimes(vault_root: Path) -> dict[str, float]:
    if not vault_root.exists():
        return {}
    snapshot: dict[str, float] = {}
    for file_path in vault_root.rglob("*"):
        if not file_path.is_file():
            continue
        if ".obsidian" in file_path.parts:
            continue
        snapshot[str(file_path.relative_to(vault_root))] = file_path.stat().st_mtime
    return snapshot


def diff_modified_files(before: dict[str, float], after: dict[str, float]) -> set[str]:
    modified: set[str] = set()
    for relative_path, mtime in after.items():
        if relative_path not in before or before[relative_path] != mtime:
            modified.add(relative_path)
    return modified
