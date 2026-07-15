import json
from collections.abc import Iterator
from http.server import HTTPServer
from pathlib import Path

import pytest

from devscope_plugin_chatguru import server


@pytest.fixture(autouse=True)
def _reset_state() -> Iterator[None]:
    yield
    server._state = None


def test_get_service_health_requires_initialized_state() -> None:
    with pytest.raises(RuntimeError):
        server.get_service_health()


def test_get_service_health_records_audit_on_success(
    tmp_path: Path, health_server: HTTPServer
) -> None:
    base_url = f"http://127.0.0.1:{health_server.server_port}"
    server._state = server.PluginContext(
        project_root=tmp_path, profile="read-only", chatguru_base_url=base_url
    )

    result = server.get_service_health()

    assert result["status"] == "ok"
    audit_path = tmp_path / ".devscope" / "logs" / "audit.jsonl"
    lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["plugin"] == "chatguru"
    assert entry["action"] == "get_service_health"
    assert entry["kind"] == "read"
    assert entry["outcome"] == "executed"


def test_get_service_health_allowed_in_every_profile(
    tmp_path: Path, health_server: HTTPServer
) -> None:
    base_url = f"http://127.0.0.1:{health_server.server_port}"
    for profile in ("read-only", "development", "review"):
        server._state = server.PluginContext(
            project_root=tmp_path, profile=profile, chatguru_base_url=base_url
        )

        result = server.get_service_health()

        assert result["status"] == "ok"
