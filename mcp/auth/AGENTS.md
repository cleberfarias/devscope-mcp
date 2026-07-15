# DevScope Auth — instruções para agentes

Componente `mcp/auth` do monorepo DevScope. Regras válidas para o repositório
inteiro estão em [../../AGENTS.md](../../AGENTS.md).

## Objetivo

Implementar o modelo de permissão e auditoria desenhado em
[../../docs/architecture/permissions.md](../../docs/architecture/permissions.md).
Toda ação de qualquer plugin em `mcp/plugins/*` passa por aqui antes de executar.

## Regras obrigatórias

- `authorize()` é a única função que decide se uma ação roda, é bloqueada ou
  precisa de confirmação — nenhum plugin deve reimplementar essa lógica
  localmente.
- Toda chamada a uma ação de plugin grava uma entrada em auditoria via
  `AuditLog`, mesmo quando bloqueada.
- Nenhuma credencial pode ser aceita como parâmetro de ação para começar de
  conversa — a redação de `_redact` em `audit.py` é uma segunda camada de defesa,
  não a primeira.
- Mudança na matriz perfil x kind exige atualizar
  `docs/architecture/permissions.md` no mesmo commit — a tabela lá e o código
  aqui precisam continuar batendo.

## Arquitetura

- `manifest.py`: `ActionKind`, `ActionManifest` — como uma ação se declara.
- `authorize.py`: a matriz perfil x kind, `Decision`.
- `audit.py`: `AuditLog`, escrita append-only em JSONL, redação de segredos.

Ainda não implementado (ver "roadmap" em permissions.md): o protocolo de
confirmação de duas etapas (`confirmation_token` / `confirm_action`) para ações
`write_destructive`. Não crie esse mecanismo especulativamente — implemente
quando o primeiro plugin com uma ação `write_destructive` real existir, para não
desenhar um protocolo sem nada que o exercite de ponta a ponta.

## Validação

1. `ruff check .`
2. `mypy`
3. `pytest`
