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
   `mcp/server` (somente leitura) mais `mcp/auth` (implementação do modelo de
   permissão e auditoria de [permissions.md](permissions.md)) e o primeiro plugin,
   `mcp/plugins/chatguru`, com uma única ação de leitura
   (`get_service_health`). Ações de escrita e os demais sistemas (Docker, Kafka,
   Redis, Postgres, GitHub, Sentry) continuam roadmap.
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
parte. AGENTS.md e Skills alimentam o pilar Knowledge; `mcp/server`, `mcp/auth` e
`mcp/plugins/chatguru` implementam o pilar Execution hoje.

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
| Execution | `mcp/server` (read-only), `mcp/auth`, `mcp/plugins/chatguru` (1 ação de leitura) | Mais ações do ChatGuru; plugins para Docker, Kafka, Redis, Postgres, GitHub, Sentry |
| Observability | — | Logs, métricas, incidentes |
| Architecture Intelligence | `scan_project`, `analyze_current_branch` | Grafo de dependências, análise de impacto |
| DX | CLI (`devscope doctor/init/scan/upgrade`), `.vscode/mcp.json` | SDK, integração CI/CD mais profunda |

## Roadmap por fases

- **Fase 1 — Fundação** (em andamento): `AGENTS.md`, documentação de arquitetura,
  primeiras Skills reais.
- **Fase 2 — Core** (em andamento): `mcp/auth` implementa o modelo de permissão e
  auditoria de [permissions.md](permissions.md); `mcp/plugins/chatguru` tem a
  primeira ação real (`get_service_health`, leitura). Faltam: mais ações do
  ChatGuru (incluindo a primeira ação de escrita, que vai exercitar o protocolo de
  confirmação ainda não implementado), outros plugins, SDK e expansão da CLI.
- **Fase 3 — Conhecimento**: RAG, playbooks, runbooks, ADRs.
- **Fase 4 — Interface**: dashboard web (saúde do projeto, diagnósticos, arquitetura,
  agentes).
- **Fase 5 — Enterprise**: multi-organização, marketplace de plugins e Skills,
  versionamento, observabilidade completa, permissões, times, auditoria.

Cada fase só começa quando a anterior tem conteúdo real publicado — não se cria a
estrutura de pastas de uma fase futura antecipadamente.

## Primeiro caso real de plugin (Fase 2)

O primeiro plugin de execução é o **ChatGuru** (`mcp/plugins/chatguru`), construído
do zero — não é um wrapper de nenhum servidor MCP ChatGuru já existente em outro
projeto. Hoje ele tem uma única ação, `get_service_health` (leitura), que já passa
pelo fluxo completo de `authorize()` + `AuditLog` de `mcp/auth`. O objetivo dela foi
validar o mecanismo de registro de plugin + permissão + auditoria de ponta a ponta
antes de expandir para APIs, containers, Docker, banco de dados, filas, telefones,
bots e fluxos daquele produto — inclusive a primeira ação de escrita, que vai exigir
implementar o protocolo de confirmação de duas etapas ainda pendente em `mcp/auth`.
