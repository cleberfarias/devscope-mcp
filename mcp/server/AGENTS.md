# DevScope MCP — instruções para agentes

Componente `mcp/server` do monorepo DevScope. Regras válidas para o repositório
inteiro estão em [../../AGENTS.md](../../AGENTS.md); as regras abaixo são
específicas deste componente e têm precedência dentro desta pasta.

## Objetivo

Construir um servidor MCP somente leitura que entregue contexto verificável sobre código, Git e regras do projeto.

## Regras obrigatórias

- Não criar ferramentas genéricas de execução de shell.
- Não modificar arquivos do projeto analisado.
- Não executar `git reset`, `git checkout`, `git clean`, `git push` ou comandos equivalentes.
- Toda conclusão sobre código deve incluir arquivo, linha ou outra evidência quando possível.
- Nunca escrever logs em stdout durante o transporte stdio; usar stderr.
- Caminhos recebidos devem permanecer dentro da raiz configurada.

## Arquitetura

- `server.py`: ligação com o protocolo MCP e registro das ferramentas.
- `services/`: lógica testável sem dependência direta do protocolo.
- `models/`: contratos Pydantic.
- `security/`: validação de caminhos e futuras políticas.
- `cache.py`: `TTLCache` genérico. Hoje só `scan_project` usa (30s de TTL) — troca
  deliberada entre não reescanear o projeto inteiro a cada chamada e tolerar alguns
  segundos de desatualização. `search_code_context` propositalmente não usa cache:
  resultado de busca é citado como evidência de arquivo/linha, e desatualização ali
  é um risco de correção, não só de performance.

## Validação

Antes de concluir uma mudança:

1. Executar `ruff check .`.
2. Executar `mypy` (modo strict; todo módulo novo precisa de tipos completos).
3. Executar `pytest`.
4. Verificar se o servidor importa corretamente.
5. Confirmar que nenhum `print()` operacional escreve em stdout.

A CI (`.github/workflows/ci.yml`) roda os passos 1–4 em Ubuntu, Windows e macOS a
cada push/PR na `master`. Uma mudança que falha localmente falha lá também.
