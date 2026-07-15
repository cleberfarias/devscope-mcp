# DevScope

[![CI](https://github.com/cleberfarias/devscope-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/cleberfarias/devscope-mcp/actions/workflows/ci.yml)

Plataforma de inteligência de engenharia para agentes de IA. O objetivo é que um
agente (GitHub Copilot, Claude Code, Codex, Cursor, VS Code Agent etc.) entenda um
projeto de software — arquitetura, convenções, histórico e infraestrutura — sem
precisar reconstruir esse contexto a cada conversa.

Veja o desenho completo em [docs/architecture/overview.md](docs/architecture/overview.md).

## O que existe hoje

| Componente | Pasta | Status |
|---|---|---|
| Servidor MCP (leitura de projeto, Git, busca de código) | [mcp/server](mcp/server) | Funcional, publicado como `devscope-mcp` |
| Skills (conhecimento de domínio) | [skills](skills) | Em construção — 2 skills reais |
| Documentação de arquitetura | [docs/architecture](docs/architecture) | Fundação |
| Orquestrador de agente, plugins MCP adicionais, RAG, UI, SDK | — | Roadmap, ainda não iniciados |

Não existem pastas vazias reservando lugar para fases futuras — quando uma fase começa,
a pasta nasce com conteúdo real no mesmo commit.

## Instalar o servidor MCP hoje

```bash
cd mcp/server
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/WSL/macOS:    source .venv/bin/activate
pip install -e ".[dev]"
```

Instruções completas de uso, CLI e segurança em [mcp/server/README.md](mcp/server/README.md).

## Estrutura do repositório

```text
devscope/
├── AGENTS.md
├── devscope.json
├── docs/
│   └── architecture/
├── skills/
│   ├── git/
│   └── architecture/
├── mcp/
│   └── server/
└── .vscode/
```

## Licença

MIT — veja [LICENSE](LICENSE).
