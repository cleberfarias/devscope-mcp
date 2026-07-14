"""Command-line interface for configuring and inspecting DevScope projects."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from devscope import __version__
from devscope.config import load_config
from devscope.security.paths import resolve_project_root
from devscope.services.project_scanner import ProjectScanner

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str
    required: bool = False


def _run_version(command: list[str]) -> str | None:
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if process.returncode != 0:
        return None
    output = (process.stdout or process.stderr).strip().splitlines()
    return output[0] if output else "disponível"


def _tool_check(name: str, executable: str, version_args: list[str], required: bool = False) -> CheckResult:
    path = shutil.which(executable)
    if not path:
        return CheckResult(name, "missing", "não encontrado no PATH", required)
    version = _run_version([path, *version_args])
    return CheckResult(name, "ok", version or path, required)


def doctor(project_root: Path | None = None) -> dict[str, Any]:
    checks = [
        CheckResult("Sistema", "ok", f"{platform.system()} {platform.release()}"),
        CheckResult("Python", "ok", platform.python_version(), required=True),
        _tool_check("Git", "git", ["--version"], required=True),
        _tool_check("Docker", "docker", ["--version"]),
        _tool_check("Node.js", "node", ["--version"]),
        _tool_check("Ripgrep", "rg", ["--version"]),
        _tool_check("VS Code", "code", ["--version"]),
    ]

    project: dict[str, Any] | None = None
    if project_root is not None:
        config_path = project_root / "devscope.json"
        project = {
            "root": str(project_root),
            "devscope_config": config_path.exists(),
            "agents_file": (project_root / "AGENTS.md").exists(),
            "vscode_mcp": (project_root / ".vscode" / "mcp.json").exists(),
            "git_repository": (project_root / ".git").exists(),
        }

    required_ok = all(item.status == "ok" for item in checks if item.required)
    return {
        "devscope_version": __version__,
        "ready": required_ok,
        "checks": [asdict(item) for item in checks],
        "project": project,
    }


def _detect_base_branch(root: Path) -> str:
    if not (root / ".git").exists() or not shutil.which("git"):
        return "main"
    for candidate in ("development", "main", "master"):
        process = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{candidate}"],
            cwd=root,
            timeout=5,
            check=False,
        )
        if process.returncode == 0:
            return candidate
    return "main"


def _write_text(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return "skipped"
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "updated" if existed else "created"


def _write_json(path: Path, data: dict[str, Any], force: bool) -> str:
    if path.exists() and not force:
        return "skipped"
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return "updated" if existed else "created"


def init_project(root: Path, base_branch: str | None = None, force: bool = False) -> dict[str, Any]:
    branch = base_branch or _detect_base_branch(root)
    config = {
        "schemaVersion": CURRENT_SCHEMA_VERSION,
        "project": {
            "name": root.name,
            "description": "",
        },
        "git": {
            "baseBranch": branch,
            "remote": "origin",
        },
        "paths": {
            "frontend": [],
            "backend": [],
            "tests": ["tests"],
            "documentation": ["docs"],
        },
        "ignore": [
            ".git", ".venv", "venv", "node_modules", "dist", "build", "coverage",
            "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        ],
        "security": {"profile": "read-only"},
        "instructions": {"agentsFile": "AGENTS.md"},
    }
    mcp_config = {
        "servers": {
            "devscope": {
                "type": "stdio",
                "command": "devscope-mcp",
                "args": [
                    "--project-root", "${workspaceFolder}",
                    "--config", "${workspaceFolder}/devscope.json",
                ],
            }
        }
    }
    agents = f"""# Instruções para agentes\n\n## Projeto\n\nProjeto: `{root.name}`.\n\n## Git\n\n- A branch base é `{branch}`.\n- Não faça commit diretamente na branch base.\n- Analise o impacto antes de alterar componentes compartilhados.\n\n## Segurança\n\n- Não exponha credenciais, tokens ou dados sensíveis.\n- Não execute comandos destrutivos.\n- Informe claramente validações que não puderam ser executadas.\n\n## Validação\n\nAntes de concluir uma tarefa:\n\n1. Analise o diff em relação a `{branch}`.\n2. Execute verificações de sintaxe, lint e testes relacionados quando disponíveis.\n3. Informe riscos, arquivos impactados e evidências.\n"""

    results = {
        "devscope.json": _write_json(root / "devscope.json", config, force),
        ".vscode/mcp.json": _write_json(root / ".vscode" / "mcp.json", mcp_config, force),
        "AGENTS.md": _write_text(root / "AGENTS.md", agents, force),
    }
    return {"project_root": str(root), "base_branch": branch, "files": results}


def scan_project(root: Path, config_path: Path | None = None) -> dict[str, Any]:
    config = load_config(root, config_path)
    return ProjectScanner(root, config).scan().model_dump()


def upgrade_project(root: Path) -> dict[str, Any]:
    path = root / "devscope.json"
    if not path.exists():
        raise ValueError("devscope.json não encontrado. Execute `devscope init` primeiro.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"devscope.json inválido: {exc}") from exc

    previous = int(data.get("schemaVersion", 0))
    changes: list[str] = []
    if previous < 1:
        data["schemaVersion"] = 1
        data.setdefault("security", {"profile": "read-only"})
        data.setdefault("instructions", {"agentsFile": "AGENTS.md"})
        changes.append("Configuração migrada para schemaVersion 1")

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "project_root": str(root),
        "previous_schema_version": previous,
        "current_schema_version": int(data.get("schemaVersion", CURRENT_SCHEMA_VERSION)),
        "changes": changes,
        "status": "updated" if changes else "already_current",
    }


def _print_doctor(result: dict[str, Any]) -> None:
    print(f"DevScope {result['devscope_version']} — diagnóstico do ambiente\n")
    symbols = {"ok": "✔", "missing": "○", "error": "✖"}
    for check in result["checks"]:
        suffix = " (obrigatório)" if check["required"] else ""
        print(f"{symbols.get(check['status'], '•')} {check['name']}{suffix}: {check['detail']}")
    project = result.get("project")
    if project:
        print("\nProjeto:")
        for key, value in project.items():
            print(f"  {key}: {value}")
    print("\nAmbiente essencial pronto." if result["ready"] else "\nFaltam dependências obrigatórias.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="devscope", description="DevScope project intelligence CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor_parser = sub.add_parser("doctor", help="Verifica ambiente e configuração do projeto")
    doctor_parser.add_argument("--project-root", default=".")
    doctor_parser.add_argument("--json", action="store_true", dest="as_json")

    init_parser = sub.add_parser("init", help="Configura DevScope no projeto atual")
    init_parser.add_argument("--project-root", default=".")
    init_parser.add_argument("--base-branch", default=None)
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument("--json", action="store_true", dest="as_json")

    scan_parser = sub.add_parser("scan", help="Analisa tecnologias e estrutura do projeto")
    scan_parser.add_argument("--project-root", default=".")
    scan_parser.add_argument("--config", default=None)
    scan_parser.add_argument("--json", action="store_true", dest="as_json")

    upgrade_parser = sub.add_parser("upgrade", help="Atualiza a configuração para o schema atual")
    upgrade_parser.add_argument("--project-root", default=".")
    upgrade_parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        root = resolve_project_root(args.project_root)
        if args.command == "doctor":
            result = doctor(root)
            if args.as_json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                _print_doctor(result)
            raise SystemExit(0 if result["ready"] else 1)
        if args.command == "init":
            result = init_project(root, args.base_branch, args.force)
        elif args.command == "scan":
            config_path = Path(args.config).expanduser().resolve() if args.config else None
            result = scan_project(root, config_path)
        elif args.command == "upgrade":
            result = upgrade_project(root)
        else:
            raise ValueError(f"Comando desconhecido: {args.command}")

        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
