from enum import StrEnum

from devscope_auth.manifest import ActionKind, ActionManifest

PROFILES = ("read-only", "development", "review")


class Decision(StrEnum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    NEEDS_CONFIRMATION = "needs_confirmation"


def authorize(profile: str, action: ActionManifest) -> Decision:
    """Decide se uma ação de plugin roda, é bloqueada ou precisa de confirmação.

    Implementa a matriz perfil x kind de docs/architecture/permissions.md. Uma
    mudança aqui exige atualizar aquele documento no mesmo commit.
    """
    if profile not in PROFILES:
        raise ValueError(f"Perfil desconhecido: {profile}")

    if action.kind is ActionKind.READ:
        return Decision.ALLOWED

    if profile == "read-only":
        return Decision.BLOCKED

    if profile == "review":
        if action.kind is ActionKind.WRITE_REVERSIBLE and action.scope == "review":
            return Decision.ALLOWED
        return Decision.BLOCKED

    # development
    if action.kind is ActionKind.WRITE_REVERSIBLE:
        return Decision.ALLOWED
    return Decision.NEEDS_CONFIRMATION
