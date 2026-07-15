import os
import urllib.error
import urllib.request
from dataclasses import dataclass

DEFAULT_TIMEOUT_SECONDS = 5.0
HEALTH_ENDPOINT_PATH = "/api/v2/service/health"


@dataclass(frozen=True)
class ServiceHealth:
    status: str  # "ok" | "unreachable" | "error"
    detail: str


def check_service_health(
    base_url: str | None = None, timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> ServiceHealth:
    """Consulta o endpoint de saúde de um serviço ChatGuru configurado.

    `base_url` vem da configuração do plugin (não é segredo). Um eventual token
    de autenticação é lido de `CHATGURU_API_TOKEN` diretamente do ambiente do
    processo — nunca aceito como parâmetro desta função nem de uma ferramenta
    MCP, conforme docs/architecture/permissions.md.
    """
    url = base_url or os.environ.get("CHATGURU_API_BASE_URL")
    if not url:
        return ServiceHealth(
            status="unreachable", detail="CHATGURU_API_BASE_URL não configurada."
        )

    endpoint = url.rstrip("/") + HEALTH_ENDPOINT_PATH
    request = urllib.request.Request(endpoint)
    token = os.environ.get("CHATGURU_API_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="ignore")
            return ServiceHealth(status="ok", detail=body[:500])
    except urllib.error.HTTPError as exc:
        return ServiceHealth(status="error", detail=f"HTTP {exc.code} em {endpoint}")
    except urllib.error.URLError as exc:
        return ServiceHealth(status="unreachable", detail=str(exc.reason))
