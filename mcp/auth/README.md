# DevScope Auth

Componente `mcp/auth` do [monorepo DevScope](../../README.md). Implementa o modelo
de permissão e auditoria desenhado em
[docs/architecture/permissions.md](../../docs/architecture/permissions.md).

Toda ação exposta por um plugin em `mcp/plugins/*` passa por `authorize()` antes de
executar, e toda tentativa (permitida, bloqueada ou pendente de confirmação) é
registrada via `AuditLog`. Nenhum plugin reimplementa essa lógica localmente.

## Instalação para desenvolvimento

```bash
cd mcp/auth
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/WSL/macOS:    source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

```python
from devscope_auth.authorize import authorize, Decision
from devscope_auth.manifest import ActionKind, ActionManifest
from devscope_auth.audit import AuditLog

action = ActionManifest(name="get_service_health", kind=ActionKind.READ)
decision = authorize("read-only", action)  # Decision.ALLOWED

audit = AuditLog(project_root / ".devscope" / "logs" / "audit.jsonl")
audit.record(
    plugin="chatguru",
    action=action.name,
    kind=action.kind.value,
    profile="read-only",
    outcome="executed",
    project_root=str(project_root),
    parameters={},
)
```

## Desenvolvimento e validação

```bash
ruff check .
mypy
pytest
```
