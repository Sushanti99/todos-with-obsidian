from datetime import datetime

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from brain.app_config import default_app_config
from brain.env_config import load_env_config
from brain.models import BackendValidationResult
from brain.server import AppRuntime, create_app
from brain.session import SessionManager


class FakeBackend:
    def validate_installation(self):
        return BackendValidationResult(
            installed=True,
            command="fake",
            resolved_path="/usr/bin/fake",
            version="fake 1.0",
        )

    async def stream(self, prompt, cwd, env):
        yield type("Event", (), {"type": "chunk", "content": "hello", "raw": None})()
        yield type("Event", (), {"type": "chunk", "content": " world", "raw": None})()
        yield type("Event", (), {"type": "done", "content": None, "raw": None})()

    async def summarize(self, prompt, cwd, env):
        return "# Session Summary\n\n## Topics Discussed\n- test\n\n## Decisions Made\n- done\n\n## Files Modified\n- none\n\n## Action Items\n- none"


def test_status_route_and_single_websocket_enforcement(tmp_path, monkeypatch):
    app_cfg = default_app_config(tmp_path / "vault")
    env_cfg = load_env_config()
    runtime = AppRuntime(app_cfg=app_cfg, env_cfg=env_cfg, session_manager=SessionManager(app_cfg.agent))
    app = create_app(runtime)
    monkeypatch.setattr("brain.server.get_backend", lambda cfg: FakeBackend())

    client = TestClient(app)
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["agent"] == "claude-code"

    with client.websocket_connect("/ws") as ws1:
        session_payload = ws1.receive_json()
        assert session_payload["type"] == "session"

        with client.websocket_connect("/ws") as ws2:
            error_payload = ws2.receive_json()
            assert error_payload["type"] == "session_conflict"
            assert "already connected" in error_payload["message"]


def test_websocket_message_streams_response(tmp_path, monkeypatch):
    app_cfg = default_app_config(tmp_path / "vault")
    env_cfg = load_env_config()
    runtime = AppRuntime(app_cfg=app_cfg, env_cfg=env_cfg, session_manager=SessionManager(app_cfg.agent))
    app = create_app(runtime)
    monkeypatch.setattr("brain.server.get_backend", lambda cfg: FakeBackend())

    client = TestClient(app)
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json({"type": "message", "content": "Hello"})

        statuses = []
        chunks = []
        done = None
        for _ in range(4):
            payload = ws.receive_json()
            if payload["type"] == "status":
                statuses.append(payload["state"])
            elif payload["type"] == "chunk":
                chunks.append(payload["content"])
            elif payload["type"] == "done":
                done = payload

        assert "thinking" in statuses
        assert "".join(chunks) == "hello world"
        assert done["content"] == "hello world"
