# DevScope Plugin: ChatGuru

Componente `mcp/plugins/chatguru` do [monorepo DevScope](../../../README.md) —
primeiro plugin de execução da plataforma, construído do zero sobre o modelo de
permissão e auditoria de [`devscope-auth`](../../auth/README.md), seguindo o
desenho em
[docs/architecture/permissions.md](../../../docs/architecture/permissions.md).

Não é um wrapper do servidor MCP ChatGuru já existente em outros projetos — é uma
implementação independente, pensada para funcionar em qualquer projeto que
configure a URL do ChatGuru, não só no projeto de origem.

## Ferramenta MCP

- `get_service_health` — ação `read`. Consulta `GET {base_url}/api/v2/service/health`
  e reporta status (`ok` / `unreachable` / `error`). É a única ação implementada até
  agora: valida o mecanismo de registro de plugin, permissão e auditoria de ponta a
  ponta antes de expandir para outras ações do ChatGuru.

## Configuração

- `--chatguru-base-url` (CLI) ou variável de ambiente lida por quem inicia o
  processo: URL base da API. Não é segredo.
- `CHATGURU_API_TOKEN` (variável de ambiente, opcional): token de autenticação,
  lido diretamente do ambiente do processo dentro de `health.py` — nunca aceito
  como parâmetro de CLI ou de ferramenta MCP.

## Instalação para desenvolvimento

`devscope-auth` ainda não está publicado — instale-o em modo editável primeiro,
na mesma virtualenv:

```bash
cd mcp/auth
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/WSL/macOS:    source .venv/bin/activate
pip install -e ".[dev]"

cd ../plugins/chatguru
pip install -e ".[dev]"
```

## Uso manual

```bash
devscope-plugin-chatguru --project-root . --profile read-only --chatguru-base-url https://chatguru.exemplo.com
```

## Desenvolvimento e validação

```bash
ruff check .
mypy
pytest
```
