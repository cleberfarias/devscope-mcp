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
    ├── server/         servidor MCP read-only (AGENTS.md próprio em mcp/server/AGENTS.md)
    ├── auth/           permissão e auditoria para plugins (AGENTS.md em mcp/auth/AGENTS.md)
    └── plugins/
        └── chatguru/   primeiro plugin de execução (AGENTS.md em mcp/plugins/chatguru/AGENTS.md)
```

`mcp/plugins/chatguru` hoje tem uma única ação (`get_service_health`, leitura) —
existe para validar o mecanismo de registro de plugin, permissão e auditoria de ponta
a ponta, não como implementação completa do ChatGuru. Pastas restantes do roadmap
(`rag/`, `ui/`, `sdk/`) ainda não existem. Não crie stubs vazios para elas — cada uma
nasce quando sua fase começar, com conteúdo real desde o primeiro commit. Consulte
`docs/architecture/overview.md` para o roadmap completo antes de assumir que uma fase
futura já começou.

## Regras obrigatórias

- Não adicionar pastas ou arquivos de fases futuras do roadmap sem decisão explícita
  registrada em `docs/architecture/overview.md`.
- Toda Skill nova precisa ser conhecimento real e verificável, nunca um placeholder
  ("TODO", "em breve"). Se não há conteúdo genuíno para uma Skill ainda, ela não deve
  ser criada.
- Toda ação de qualquer plugin em `mcp/plugins/*` que toque sistema externo (Docker,
  Kafka, Redis, Postgres, GitHub, Sentry, ChatGuru etc.) segue o modelo de permissão
  e auditoria definido em
  [docs/architecture/permissions.md](docs/architecture/permissions.md), implementado
  em `mcp/auth`. Nenhuma ação nova é aceita sem passar pelo checklist no final desse
  documento.
- O componente `mcp/server/` permanece somente leitura; suas regras próprias estão em
  `mcp/server/AGENTS.md` e têm precedência para qualquer mudança dentro dessa pasta.

## Validação

Antes de concluir uma mudança em qualquer componente, execute a validação específica
descrita no `AGENTS.md` daquele componente (por exemplo, `mcp/server/AGENTS.md` define
`ruff check .`, `pytest` e a checagem de import do servidor).
