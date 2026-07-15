# DevScope MCP

Componente `Execution` da [DevScope AI Platform](../../README.md) — veja
[docs/architecture/overview.md](../../docs/architecture/overview.md) para como este
servidor se encaixa nos outros pilares.

O DevScope fornece contexto confiável de um projeto para agentes de IA no VS Code. Ele analisa tecnologias, estrutura, regras do `AGENTS.md`, branch atual e código-fonte sem permitir comandos arbitrários.

## Sistemas suportados

- Windows 10/11
- WSL
- Linux
- macOS

A configuração gerada é a mesma em todos os sistemas. O VS Code inicia o comando `devscope-mcp`, instalado no PATH pelo Python.

## Requisitos

- Python 3.11 ou superior
- Git
- VS Code com suporte a MCP

Docker, Node.js e Ripgrep são opcionais. O comando `doctor` informa o que está disponível.

## Instalação para desenvolvimento

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Linux, WSL ou macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

A instalação cria dois comandos:

```text
devscope      CLI de configuração e diagnóstico
devscope-mcp  servidor MCP usado pelo VS Code
```

## Uso em outro projeto

Entre na pasta do projeto que receberá o DevScope:

```bash
cd caminho/do/meu-projeto
devscope init
```

O comando cria, sem sobrescrever arquivos existentes:

```text
devscope.json
AGENTS.md
.vscode/mcp.json
```

Para definir manualmente a branch base:

```bash
devscope init --base-branch development
```

Para substituir arquivos já existentes conscientemente:

```bash
devscope init --force
```

Depois, abra a pasta no VS Code:

```bash
code .
```

No VS Code, execute `MCP: List Servers`, selecione `devscope` e inicie o servidor.

## Comandos da CLI

### Diagnosticar o ambiente

```bash
devscope doctor
```

Verifica:

- sistema operacional;
- Python;
- Git;
- Docker;
- Node.js;
- Ripgrep;
- VS Code;
- presença de `devscope.json`, `AGENTS.md` e `.vscode/mcp.json`.

Saída em JSON:

```bash
devscope doctor --json
```

### Configurar um projeto

```bash
devscope init
```

A configuração gerada usa este servidor MCP:

```json
{
  "servers": {
    "devscope": {
      "type": "stdio",
      "command": "devscope-mcp",
      "args": [
        "--project-root",
        "${workspaceFolder}",
        "--config",
        "${workspaceFolder}/devscope.json"
      ]
    }
  }
}
```

Não existem caminhos fixos como `C:\\Users\\...` ou `/home/...`, por isso o arquivo funciona para toda a equipe.

### Analisar o projeto

```bash
devscope scan
```

Identifica linguagens, frameworks, gerenciadores de pacotes, testes, Docker, CI e arquivos importantes.

### Atualizar a configuração

```bash
devscope upgrade
```

Migra `devscope.json` para a versão atual do schema sem alterar código do projeto.

## Ferramentas MCP

- `health_check`
- `scan_project`
- `analyze_current_branch`
- `search_code_context`
- `get_task_context`

Exemplos no chat do agente:

```text
Use o DevScope para analisar este projeto.
```

```text
Use o DevScope para comparar minha branch atual com development.
```

```text
Use o DevScope para montar o contexto da tarefa de bloquear contas trial expiradas.
```

## Segurança

O MVP funciona em modo somente leitura:

- não altera código;
- não cria commits;
- não faz push;
- não executa comandos fornecidos livremente pelo agente;
- restringe buscas à pasta do projeto;
- usa apenas comandos Git previamente permitidos.

## Desenvolvimento e validação

```bash
pytest
ruff check .
python -m compileall src tests
```

Para iniciar o servidor manualmente:

```bash
devscope-mcp --project-root .
```

Para mostrar a configuração resolvida sem iniciar o MCP:

```bash
devscope-mcp --project-root . --print-config
```
