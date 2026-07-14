import json
from pathlib import Path

from devscope.models.config import DevScopeConfig


def load_config(project_root: Path, config_path: Path | None = None) -> DevScopeConfig:
    path = config_path or project_root / "devscope.json"
    if not path.exists():
        return DevScopeConfig()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Configuração JSON inválida em {path}: {exc}") from exc

    return DevScopeConfig.model_validate(data)
