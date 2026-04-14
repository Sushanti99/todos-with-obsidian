"""Daily-note integration context collection."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from datetime import date
from pathlib import Path

from brain.models import AppConfig, DailyContext, EnvConfig
from brain.vault import read_vault


def build_daily_context(app_cfg: AppConfig, env_cfg: EnvConfig) -> DailyContext:
    legacy_config = _load_legacy_module("config")
    _configure_legacy_modules(legacy_config, app_cfg, env_cfg)
    bundle = DailyContext(today=date.today().isoformat())

    try:
        all_notes = read_vault(app_cfg.vault.path)
        bundle.vault_notes = [note for note in all_notes if not note.frontmatter.get("generated")]
    except Exception:
        bundle.vault_notes = []

    try:
        calendar_client = _load_legacy_module("calendar_client")

        bundle.calendar_events = calendar_client.get_todays_events()
    except Exception:
        bundle.calendar_events = []

    try:
        gmail_client = _load_legacy_module("gmail_client")

        bundle.email_items = gmail_client.get_action_items()
    except Exception:
        bundle.email_items = []

    try:
        notion_client = _load_legacy_module("notion_client")

        bundle.notion_tasks = notion_client.get_open_tasks()
    except Exception:
        bundle.notion_tasks = []

    if app_cfg.integrations.include_reading_list_in_daily_note:
        try:
            news_client = _load_legacy_module("news_client")

            bundle.reading_list = news_client.get_reading_list(bundle.vault_notes)
        except Exception:
            bundle.reading_list = []

    return bundle


def _configure_legacy_modules(legacy_config, app_cfg: AppConfig, env_cfg: EnvConfig) -> None:
    legacy_config.VAULT_PATH = app_cfg.vault.path
    legacy_config.DAILY_FOLDER = app_cfg.vault.daily_folder
    legacy_config.GOOGLE_CREDENTIALS_FILE = env_cfg.google_credentials_file
    legacy_config.GOOGLE_TOKEN_FILE = env_cfg.google_token_file
    legacy_config.NOTION_API_KEY = env_cfg.notion_api_key
    legacy_config.NEWS_FEEDS = ",".join(env_cfg.news_feeds)


def _load_legacy_module(module_name: str):
    if module_name in sys.modules:
        return sys.modules[module_name]

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        module_path = _legacy_module_path(module_name)
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


def _legacy_module_path(module_name: str) -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / f"{module_name}.py"
