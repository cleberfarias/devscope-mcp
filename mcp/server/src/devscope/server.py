import argparse
import json
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from devscope import __version__
from devscope.cache import TTLCache
from devscope.config import load_config
from devscope.context import AppContext
from devscope.security.paths import resolve_project_root
from devscope.services.code_search import CodeSearch
from devscope.services.git_service import GitService
from devscope.services.keywords import extract_keywords
from devscope.services.project_scanner import ProjectScanner

mcp = FastMCP("DevScope MCP")
_app: AppContext | None = None

SCAN_CACHE_TTL_SECONDS = 30
_scan_cache: TTLCache[dict[str, Any]] = TTLCache(ttl_seconds=SCAN_CACHE_TTL_SECONDS)


def app() -> AppContext:
    if _app is None:
        raise RuntimeError("DevScope não foi inicializado.")
    return _app


@mcp.tool()
def health_check() -> dict[str, str]:
    """Verifica se o DevScope MCP está funcionando e mostra o projeto ativo."""
    ctx = app()
    return {
        "status": "ok",
        "server": "devscope-mcp",
        "version": __version__,
        "project_root": str(ctx.project_root),
        "security_profile": ctx.config.security.profile,
    }


@mcp.tool()
def scan_project() -> dict[str, Any]:
    """Mapeia linguagens, frameworks, testes, infraestrutura e arquivos importantes."""
    cached = _scan_cache.get()
    if cached is not None:
        return cached
    ctx = app()
    result = ProjectScanner(ctx.project_root, ctx.config).scan().model_dump()
    _scan_cache.set(result)
    return result


@mcp.tool()
def analyze_current_branch(base_branch: str | None = None) -> dict[str, Any]:
    """Analisa a branch atual em relação à branch base configurada, sem modificar o Git."""
    ctx = app()
    base = base_branch or ctx.config.git.base_branch
    return GitService(ctx.project_root).analyze(base).model_dump()


@mcp.tool()
def search_code_context(query: str, path: str = ".", max_results: int = 50) -> dict[str, Any]:
    """Busca texto no código do projeto e retorna arquivo, linha e trecho como evidência."""
    ctx = app()
    return CodeSearch(ctx.project_root, ctx.config).search(query, path, max_results).model_dump()


@mcp.tool()
def get_task_context(task: str, keywords: list[str] | None = None) -> dict[str, Any]:
    """Monta contexto inicial de tarefa usando projeto, regras, Git e buscas por palavra-chave."""
    ctx = app()
    result: dict[str, Any] = {
        "task": task,
        "project": scan_project(),
        "instructions": None,
        "branch": None,
        "searches": [],
        "warnings": [],
    }

    agents_file = ctx.project_root / ctx.config.instructions.agents_file
    if agents_file.exists():
        result["instructions"] = {
            "file": str(agents_file.relative_to(ctx.project_root)),
            "content": agents_file.read_text(encoding="utf-8", errors="ignore")[:12000],
        }
    else:
        missing = ctx.config.instructions.agents_file
        result["warnings"].append(f"Arquivo de instruções não encontrado: {missing}")

    try:
        base_branch = ctx.config.git.base_branch
        result["branch"] = GitService(ctx.project_root).analyze(base_branch).model_dump()
    except (ValueError, RuntimeError) as exc:
        result["warnings"].append(str(exc))

    terms = keywords or extract_keywords(task)
    searcher = CodeSearch(ctx.project_root, ctx.config)
    for term in terms:
        search = searcher.search(term, max_results=10)
        if search.matches:
            result["searches"].append(search.model_dump())

    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DevScope MCP server")
    parser.add_argument("--project-root", default=".", help="Diretório raiz do projeto analisado")
    parser.add_argument("--config", default=None, help="Caminho opcional para devscope.json")
    parser.add_argument(
        "--print-config", action="store_true", help="Mostra a configuração resolvida e encerra"
    )
    return parser.parse_args(argv)


def main() -> None:
    global _app
    args = parse_args()
    root = resolve_project_root(args.project_root)
    config_path = Path(args.config).expanduser().resolve() if args.config else None
    config = load_config(root, config_path)
    _app = AppContext(project_root=root, config=config)

    if args.print_config:
        print(json.dumps(config.model_dump(by_alias=True), indent=2, ensure_ascii=False))
        return

    # Em stdio, stdout é reservado ao protocolo MCP. Logs devem ir para stderr.
    print(f"DevScope MCP {__version__} | projeto: {root}", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
