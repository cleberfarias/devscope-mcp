from pathlib import Path


class PathSecurityError(ValueError):
    """Raised when a path escapes the configured project root."""


def resolve_project_root(raw_path: str | Path) -> Path:
    root = Path(raw_path).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"Diretório não encontrado: {root}")
    if not root.is_dir():
        raise ValueError(f"O caminho não é um diretório: {root}")
    return root


def resolve_inside_root(root: Path, raw_path: str | Path) -> Path:
    candidate = (root / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PathSecurityError(f"Caminho fora do projeto bloqueado: {candidate}") from exc
    return candidate
