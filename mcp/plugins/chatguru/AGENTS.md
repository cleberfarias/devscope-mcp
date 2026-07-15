# DevScope Plugin ChatGuru — instruções para agentes

Componente `mcp/plugins/chatguru` do monorepo DevScope. Regras válidas para o
repositório inteiro estão em [../../../AGENTS.md](../../../AGENTS.md); as regras de
[../../auth/AGENTS.md](../../auth/AGENTS.md) também se aplicam a toda ação
implementada aqui.

## Objetivo

Primeiro plugin de execução real da plataforma — implementação independente,
inspirada nas categorias de ferramentas de um servidor MCP ChatGuru já existente
em outro projeto, mas sem depender dele ou reexportar seu código.

## Regras obrigatórias

- Toda ferramenta MCP nova aqui precisa de um `ActionManifest` com `kind`
  explícito, e a chamada real precisa passar por `authorize()` e `AuditLog`
  antes de tocar em qualquer sistema externo — sem exceção, mesmo para ações
  `read`.
- Nenhuma credencial (token, senha, chave) é aceita como parâmetro de CLI ou de
  ferramenta MCP. Credenciais são lidas de variável de ambiente diretamente na
  camada que faz a chamada externa (ex.: `CHATGURU_API_TOKEN` em `health.py`).
- Uma ação nova só entra depois que a anterior está testada e validada — não
  adicione várias ações de uma vez sem cobertura de teste correspondente.
- Antes de adicionar uma ação `write_reversible` ou `write_destructive`, releia
  o checklist no fim de
  [docs/architecture/permissions.md](../../../docs/architecture/permissions.md).

## Arquitetura

- `server.py`: registro das ferramentas MCP e ligação com `devscope_auth`.
- `health.py`: lógica de negócio de cada ação, sem dependência do protocolo MCP —
  testável isoladamente.

## Validação

1. `ruff check .`
2. `mypy`
3. `pytest`
4. Verificar se o plugin importa corretamente (`python -c "from devscope_plugin_chatguru import server"`).
