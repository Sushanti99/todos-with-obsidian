import asyncio

from brain.session import SessionManager


def test_session_manager_lifecycle():
    manager = SessionManager("claude-code")

    async def run():
        websocket = object()
        session = await manager.attach_websocket(websocket)
        assert session.websocket_connected is True
        manager.add_turn("user", "hello")
        task = asyncio.create_task(asyncio.sleep(0))
        manager.mark_running(task)
        await asyncio.sleep(0)
        manager.finish_run("world", {"daily/2026-04-11.md"})
        assert manager.current_session().history[-1].content == "world"
        assert "daily/2026-04-11.md" in manager.current_session().modified_files
        await manager.detach_websocket(websocket)
        closed = manager.close_session()
        assert closed.session_id == "2026-04-11-session-1"
        assert manager.current_session() is None

    asyncio.run(run())
