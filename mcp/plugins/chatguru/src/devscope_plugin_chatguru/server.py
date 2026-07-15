import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devscope_auth.audit import AuditLog
from devscope_auth.authorize import Decision, authorize
from devscope_auth.manifest import ActionKind, ActionManifest
from mcp.server.fastmcp import FastMCP

from devscope_plugin_chatguru import __version__
from devscope_plugin_chatguru.health import check_service_health
from devscope_plugin_chatguru.security import validate_base_url

mcp = FastMCP("DevScope Plugin: ChatGuru")

GET_SERVICE_HEALTH = ActionManifest(name="get_service_health", kind=ActionKind.READ)


@dataclass(frozen=True)
class PluginContext:
    project_root: Path
    profile: str
    chatguru_base_url: str | None


_state: PluginContext | None = None


def state() -> PluginContext:
    if _state is None:
        raise RuntimeError("Plugin ChatGuru não foi inicializado.")
    return _state


def _audit_log(ctx: PluginContext) -> AuditLog:
    return AuditLog(ctx.project_root / ".devscope" / "logs" / "audit.jsonl")


@mcp.tool()
def get_service_health() -> dict[str, Any]:
    """Consulta a saúde do serviço ChatGuru configurado (ação de leitura)."""
    ctx = state()
    decision = authorize(ctx.profile, GET_SERVICE_HEALTH)
    audit = _audit_log(ctx)

    if decision is Decision.BLOCKED:
        audit.record(
            plugin="chatguru",
            action=GET_SERVICE_HEALTH.name,
            kind=GET_SERVICE_HEALTH.kind.value,
            profile=ctx.profile,
            outcome="blocked",
            project_root=str(ctx.project_root),
            parameters={},
        )
        raise PermissionError(f"Ação bloqueada pelo perfil '{ctx.profile}'.")

    result = check_service_health(ctx.chatguru_base_url)
    audit.record(
        plugin="chatguru",
        action=GET_SERVICE_HEALTH.name,
        kind=GET_SERVICE_HEALTH.kind.value,
        profile=ctx.profile,
        outcome="executed",
        project_root=str(ctx.project_root),
        parameters={},
    )
    return {"status": result.status, "detail": result.detail}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DevScope plugin: ChatGuru")
    parser.add_argument("--project-root", default=".", help="Diretório raiz do projeto analisado")
    parser.add_argument(
        "--profile",
        default="read-only",
        choices=("read-only", "development", "review"),
        help="Perfil de permissão ativo para este plugin",
    )
    parser.add_argument(
        "--chatguru-base-url",
        default=None,
        help="URL base da API do ChatGuru (não é segredo; token vem de CHATGURU_API_TOKEN)",
    )
    return parser.parse_args(argv)


def main() -> None:
    global _state
    args = parse_args()
    if args.chatguru_base_url is not None:
        validate_base_url(args.chatguru_base_url)
    _state = PluginContext(
        project_root=Path(args.project_root).expanduser().resolve(),
        profile=args.profile,
        chatguru_base_url=args.chatguru_base_url,
    )
    print(
        f"DevScope Plugin ChatGuru {__version__} | perfil: {_state.profile}",
        file=sys.stderr,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
