import ipaddress
from urllib.parse import urlparse

_BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal"}


class InvalidBaseUrlError(ValueError):
    """URL base configurada falha na política de saída HTTP do plugin."""


def validate_base_url(url: str) -> None:
    """Valida uma `base_url` configurada pelo operador (CLI ou devscope.json).

    Nunca chamada sobre um valor vindo do agente — nenhuma ferramenta MCP aceita
    URL como parâmetro (ver docs/architecture/permissions.md). Existe para reduzir
    o risco de um `devscope.json` malicioso (ex.: em repositório compartilhado)
    apontar o plugin para localhost, uma rede interna ou um endpoint de metadata
    de nuvem.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise InvalidBaseUrlError(f"URL base do ChatGuru deve usar https: {url}")

    hostname = parsed.hostname
    if not hostname:
        raise InvalidBaseUrlError(f"URL base do ChatGuru sem host válido: {url}")

    lowered = hostname.lower()
    if lowered in _BLOCKED_HOSTNAMES or lowered.endswith(".internal"):
        raise InvalidBaseUrlError(f"URL base do ChatGuru aponta para host bloqueado: {url}")

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return  # hostname textual (não é um literal de IP)

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
        raise InvalidBaseUrlError(f"URL base do ChatGuru aponta para IP bloqueado: {url}")
