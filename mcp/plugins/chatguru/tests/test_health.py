from http.server import HTTPServer

import pytest

from devscope_plugin_chatguru.health import check_service_health


def test_check_service_health_ok(health_server: HTTPServer) -> None:
    base_url = f"http://127.0.0.1:{health_server.server_port}"

    result = check_service_health(base_url=base_url)

    assert result.status == "ok"
    assert "ok" in result.detail


def test_check_service_health_missing_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHATGURU_API_BASE_URL", raising=False)

    result = check_service_health(base_url=None)

    assert result.status == "unreachable"


def test_check_service_health_http_error(health_server: HTTPServer) -> None:
    base_url = f"http://127.0.0.1:{health_server.server_port}/wrong-prefix"

    result = check_service_health(base_url=base_url)

    assert result.status == "error"
