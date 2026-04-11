"""General helpers."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path


def utc_now() -> datetime:
    return datetime.now().astimezone()


def today_iso() -> str:
    return date.today().isoformat()


def ensure_absolute_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def next_available_session_summary_path(thoughts_dir: Path, today: date | None = None) -> tuple[Path, int]:
    current_date = today or date.today()
    session = 1
    while True:
        candidate = thoughts_dir / f"{current_date.isoformat()}-session-{session}.md"
        if not candidate.exists():
            return candidate, session
        session += 1


def format_duration_minutes(started_at: datetime, ended_at: datetime) -> int:
    delta = ended_at - started_at
    return max(1, int(round(delta.total_seconds() / 60)))
