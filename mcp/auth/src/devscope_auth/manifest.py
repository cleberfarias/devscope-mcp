from dataclasses import dataclass
from enum import StrEnum


class ActionKind(StrEnum):
    """Classificação estática de uma ação de plugin.

    Ver docs/architecture/permissions.md na raiz do monorepo para a definição
    completa de cada valor e a matriz perfil x kind.
    """

    READ = "read"
    WRITE_REVERSIBLE = "write_reversible"
    WRITE_DESTRUCTIVE = "write_destructive"


@dataclass(frozen=True)
class ActionManifest:
    """Como uma ação de plugin se declara para o `authorize`.

    `scope` só importa para ações `write_reversible` avaliadas sob o perfil
    `review` — marque como `"review"` quando a ação for parte do fluxo de
    revisão de PR (ex.: comentar, aprovar), nunca para ações de infraestrutura.
    """

    name: str
    kind: ActionKind
    scope: str | None = None
