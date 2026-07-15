import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SECRET_KEY_PATTERN = re.compile(r"(token|password|secret|key|credential)", re.IGNORECASE)


def _redact(parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        key: ("***" if _SECRET_KEY_PATTERN.search(key) else value)
        for key, value in parameters.items()
    }


class AuditLog:
    """Trilha de auditoria append-only em JSONL, uma linha por tentativa de ação.

    Formato e localização (`.devscope/logs/audit.jsonl`) definidos em
    docs/architecture/permissions.md.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def record(
        self,
        *,
        plugin: str,
        action: str,
        kind: str,
        profile: str,
        outcome: str,
        project_root: str,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "plugin": plugin,
            "action": action,
            "kind": kind,
            "profile": profile,
            "outcome": outcome,
            "project_root": project_root,
            "parameters": _redact(parameters or {}),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
