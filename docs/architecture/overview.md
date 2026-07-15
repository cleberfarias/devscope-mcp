# Arquitetura da DevScope AI Platform

## Problema

Um agente de IA recebendo uma tarefa em um projeto desconhecido normalmente reconstrói,
a cada conversa, o mesmo contexto: onde fica a funcionalidade relevante, qual
arquitetura o projeto segue, quais convenções a equipe usa, qual branch comparar, quais
testes rodar, o que uma mudança pode afetar. Isso custa tokens, tempo e gera respostas
inconsistentes entre sessões.

A DevScope existe para eliminar essa reconstrução repetida, dando ao agente contexto
estruturado e verificável em vez de deixá-lo inferir tudo a partir de busca textual.

## Os seis pilares

```text
                         +----------------------+
                         |      AI Agent        |
                         |    (orquestrador)     |
                         +----------+-----------+
                                    |
        --------------------------------------------------------
        |            |            |            |               |
   AI Agents     Knowledge    Execution   Observability   Architecture
  (orquestração)   (RAG,      (MCP e         (logs,        Intelligence
                 documentação,  plugins)     métricas,      (dependências,
                    ADRs)                    incidentes)     impacto)
                                    |
                                    |
                          Developer Experience (DX)
                       (VS Code, CLI, GitHub, CI/CD)
```

1. **AI Agents** — orquestração: entende a solicitação, decide quais Skills e
   ferramentas usar, combina resultados. Não executa ações diretamente.
2. **Knowledge** — memória técnica do projeto: documentação, ADRs, RFCs, runbooks,
   playbooks. Hoje representado por `docs/` e pelo próprio `AGENTS.md` de cada
   componente. RAG (busca semântica sobre esse conteúdo) é roadmap, não implementado.
3. **Execution** — ferramentas que executam ações reais e controladas. Hoje é o
   `mcp/server`, somente leitura. Plugins adicionais (Docker, Kafka, Redis, Postgres,
   GitHub, Sentry, ChatGuru) são roadmap e exigem modelo de permissão e auditoria
   próprios antes de existir — não são uma extensão trivial do servidor read-only atual.
4. **Observability** — logs, métricas, tracing e saúde de sistemas. Roadmap.
5. **Architecture Intelligence** — entendimento automático de arquitetura,
   dependências e impacto de mudanças. Parcialmente coberto hoje pelo
   `scan_project` e `analyze_current_branch` do `mcp/server`; grafo de dependências
   e análise de impacto multi-módulo são roadmap.
6. **Developer Experience (DX)** — integração com VS Code, CLI, GitHub e CI/CD. Hoje
   coberto pela CLI do `mcp/server` (`devscope doctor/init/scan/upgrade`) e por
   `.vscode/mcp.json`.

Esses seis pilares substituem a divisão anterior em "quatro componentes técnicos"
(AGENTS.md, Skills, RAG, MCP Server) porque descrevem a plataforma pelo valor que
entrega a uma equipe de engenharia, não pela peça de software que implementa cada
parte. AGENTS.md e Skills alimentam o pilar Knowledge; o MCP Server é hoje o único
pilar Execution implementado.

## Fluxo

```text
Usuário
   │
   ▼
AI Agent
   │
   ├── consulta AGENTS.md (regras do projeto)
   ├── consulta Skills (conhecimento de domínio)
   ├── consulta Knowledge/RAG (quando existir)
   └── executa ferramentas via MCP
   │
   ▼
Resposta com evidência (arquivo, linha, comando executado)
```

## Estado atual vs. roadmap

| Pilar | Hoje | Roadmap |
|---|---|---|
| AI Agents | — | Orquestrador dedicado |
| Knowledge | `docs/`, `AGENTS.md` por componente | RAG com embeddings e ingestion |
| Execution | `mcp/server` (read-only) | `mcp/plugins/*` (Docker, Kafka, Redis, Postgres, GitHub, Sentry, ChatGuru) |
| Observability | — | Logs, métricas, incidentes |
| Architecture Intelligence | `scan_project`, `analyze_current_branch` | Grafo de dependências, análise de impacto |
| DX | CLI (`devscope doctor/init/scan/upgrade`), `.vscode/mcp.json` | SDK, integração CI/CD mais profunda |

## Roadmap por fases

- **Fase 1 — Fundação** (em andamento): `AGENTS.md`, documentação de arquitetura,
  primeiras Skills reais.
- **Fase 2 — Core**: `mcp/plugins/*`, SDK, expansão da CLI.
- **Fase 3 — Conhecimento**: RAG, playbooks, runbooks, ADRs.
- **Fase 4 — Interface**: dashboard web (saúde do projeto, diagnósticos, arquitetura,
  agentes).
- **Fase 5 — Enterprise**: multi-organização, marketplace de plugins e Skills,
  versionamento, observabilidade completa, permissões, times, auditoria.

Cada fase só começa quando a anterior tem conteúdo real publicado — não se cria a
estrutura de pastas de uma fase futura antecipadamente.

## Primeiro caso real de plugin (Fase 2)

O primeiro plugin de execução planejado é o **ChatGuru**, cobrindo APIs, containers,
Docker, banco de dados, filas, telefones, bots, fluxos e observabilidade daquele
produto, sem alterar o core da plataforma. Ele serve como validação de que o modelo
de plugins da Fase 2 funciona para um caso real antes de generalizar para outros
sistemas.
