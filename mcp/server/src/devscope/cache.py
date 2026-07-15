import time
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class TTLCache(Generic[T]):
    """Cache de um único valor com expiração por tempo.

    Usado para evitar reescanear o projeto inteiro a cada chamada de ferramenta
    MCP dentro da mesma sessão do servidor. Um TTL curto é uma troca deliberada:
    tolera alguns segundos de desatualização em favor de não repetir uma
    varredura completa quando o agente encadeia várias chamadas seguidas.
    """

    ttl_seconds: float
    _value: T | None = field(default=None, init=False, repr=False)
    _expires_at: float = field(default=0.0, init=False, repr=False)

    def get(self) -> T | None:
        if self._value is not None and time.monotonic() < self._expires_at:
            return self._value
        return None

    def set(self, value: T) -> None:
        self._value = value
        self._expires_at = time.monotonic() + self.ttl_seconds

    def clear(self) -> None:
        self._value = None
        self._expires_at = 0.0
