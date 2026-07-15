import json
from pathlib import Path

from devscope_auth.audit import AuditLog


def test_records_jsonl_entry(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "logs" / "audit.jsonl")

    log.record(
        plugin="chatguru",
        action="get_service_health",
        kind="read",
        profile="read-only",
        outcome="executed",
        project_root=str(tmp_path),
        parameters={"foo": "bar"},
    )

    lines = log.path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["plugin"] == "chatguru"
    assert entry["action"] == "get_service_health"
    assert entry["outcome"] == "executed"
    assert entry["parameters"] == {"foo": "bar"}
    assert "timestamp" in entry


def test_redacts_secret_like_keys(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "audit.jsonl")

    log.record(
        plugin="x",
        action="y",
        kind="read",
        profile="read-only",
        outcome="executed",
        project_root=".",
        parameters={"api_token": "sk-abc123", "container": "web-1"},
    )

    entry = json.loads(log.path.read_text(encoding="utf-8").strip())
    assert entry["parameters"]["api_token"] == "***"
    assert entry["parameters"]["container"] == "web-1"


def test_appends_multiple_entries(tmp_path: Path) -> None:
    log = AuditLog(tmp_path / "audit.jsonl")

    log.record(
        plugin="x", action="a", kind="read", profile="read-only",
        outcome="executed", project_root=".", parameters={},
    )
    log.record(
        plugin="x", action="b", kind="read", profile="read-only",
        outcome="blocked", project_root=".", parameters={},
    )

    lines = log.path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["action"] == "a"
    assert json.loads(lines[1])["outcome"] == "blocked"
