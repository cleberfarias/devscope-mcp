# DevScope — instruções para agentes

## O que é este repositório

Este é o monorepo da DevScope AI Platform. Ele reúne os componentes que juntos dão a
agentes de IA contexto confiável sobre um projeto de software: documentação viva,
especialistas de domínio (Skills) e ferramentas de execução (MCP).

Cada componente tem seu próprio `AGENTS.md` com regras específicas. Este arquivo cobre
apenas o que é válido para o repositório como um todo.

## Estrutura

```text
devscope/
├── AGENTS.md          este arquivo
├── docs/
│   └── architecture/  desenho dos pilares, decisões e roadmap
├── skills/            conhecimento de domínio consultado pelo agente
└── mcp/
    └── server/         servidor MCP read-only (AGENTS.md próprio em mcp/server/AGENTS.md)
```

Pastas descritas no roadmap (`mcp/plugins/`, `rag/`, `ui/`, `sdk/`) ainda não existem.
Não crie stubs vazios para elas — cada uma nasce quando sua fase começar, com conteúdo
real desde o primeiro commit. Consulte `docs/architecture/overview.md` para o roadmap
completo antes de assumir que uma fase futura já começou.

## Regras obrigatórias

- Não adicionar pastas ou arquivos de fases futuras do roadmap sem decisão explícita
  registrada em `docs/architecture/overview.md`.
- Toda Skill nova precisa ser conhecimento real e verificável, nunca um placeholder
  ("TODO", "em breve"). Se não há conteúdo genuíno para uma Skill ainda, ela não deve
  ser criada.
- Mudanças que executam ações reais em sistemas externos (Docker, Kafka, Redis,
  Postgres, GitHub, Sentry etc., quando `mcp/plugins/` existir) exigem um modelo de
  permissão e auditoria explícitos antes do primeiro plugin — nunca depois.
- O componente `mcp/server/` permanece somente leitura; suas regras próprias estão em
  `mcp/server/AGENTS.md` e têm precedência para qualquer mudança dentro dessa pasta.

## Validação

Antes de concluir uma mudança em qualquer componente, execute a validação específica
descrita no `AGENTS.md` daquele componente (por exemplo, `mcp/server/AGENTS.md` define
`ruff check .`, `pytest` e a checagem de import do servidor).
