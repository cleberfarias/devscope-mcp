# Modelo de permissão e auditoria para plugins de execução

Este documento é o pré-requisito exigido pelo [AGENTS.md](../../AGENTS.md) da raiz
antes de qualquer plugin em `mcp/plugins/` ser escrito: "mudanças que executam ações
reais em sistemas externos exigem um modelo de permissão e auditoria explícitos antes
do primeiro plugin — nunca depois". Ele define esse modelo. Nenhum plugin deve ser
aceito sem seguir o que está aqui.

`mcp/server` (read-only) não precisa desse modelo porque não tem ação de escrita —
ele já resolve seu próprio caso com o allowlist de comandos Git e a checagem de
caminho descritos em `mcp/server/AGENTS.md`. Este documento vale a partir do primeiro
plugin que toque um sistema externo (Docker, Kafka, Redis, Postgres, GitHub, Sentry,
ChatGuru).

## Um único conceito de permissão: os três perfis existentes

Não existe uma escala de risco separada para plugins. O `security.profile` que já
existe em `devscope.json` (`read-only`, `development`, `review`) é o único eixo de
permissão em toda a plataforma. Um plugin não introduz um novo conceito — ele declara
como suas ações se comportam dentro desses três perfis.

## Classificação obrigatória de toda ação de plugin

Toda ação exposta por um plugin como ferramenta MCP precisa declarar um `kind`:

| `kind` | Significado | Exemplo |
|---|---|---|
| `read` | Não muda estado em nenhum sistema. | Ler logs de um container, consultar status de uma fila. |
| `write_reversible` | Muda estado, mas o efeito é trivialmente desfazível ou de baixo impacto. | Reiniciar um container de desenvolvimento, reprocessar uma mensagem de fila de teste. |
| `write_destructive` | Muda estado de forma difícil ou impossível de reverter, ou afeta produção/dados de terceiros. | Deletar um tópico Kafka, dropar uma tabela, apagar um bot de produção. |

Essa classificação é estática (decidida por quem escreve o plugin, não calculada em
runtime) e faz parte do manifesto da ação — nunca inferida a partir do nome ou da
descrição da ferramenta.

## Matriz perfil × tipo de ação

| Perfil | `read` | `write_reversible` | `write_destructive` |
|---|---|---|---|
| `read-only` | permitido | bloqueado | bloqueado |
| `development` | permitido | permitido, sem confirmação | permitido, com confirmação humana obrigatória |
| `review` | permitido | permitido **somente** se a ação tiver `scope: review` (ex.: comentar ou aprovar um PR) | bloqueado |

Duas decisões deliberadas aqui:

- Em `development`, ações reversíveis rodam direto — o mesmo espírito de como
  `mcp/server` já roda leitura direto hoje, sem pedir confirmação a cada chamada.
- Em `review`, escrita fora do escopo de revisão de PR é bloqueada mesmo que seja
  reversível, porque o propósito desse perfil é estritamente revisar, não operar
  infraestrutura. Ação destrutiva nunca é permitida em `review`, mesmo com
  confirmação — não existe "confirmar" fora de `development`.

## Confirmação humana para ações destrutivas

Uma ação `write_destructive` nunca executa em uma única chamada de ferramenta MCP.
O protocolo é sempre em duas etapas:

1. O agente chama a ferramenta normalmente. Se a ação for destrutiva, o plugin **não
   executa** — retorna uma descrição do que aconteceria (`{"requires_confirmation":
   true, "confirmation_token": "...", "description": "..."}`) e nada muda no sistema
   externo.
2. Só depois que um humano vê essa descrição e decide prosseguir, o agente chama uma
   segunda ferramenta (`confirm_action(token=...)`) repassando o token. Só nesse
   segundo passo a ação é executada.

Isso existe porque o DevScope não controla a interface do agente hospedeiro (Copilot,
Claude Code, Cursor etc.) — o protocolo de duas etapas força qualquer agente a expor
a intenção a um humano antes da segunda chamada, em vez de depender de cada host
implementar sua própria confirmação.

## Trilha de auditoria

Toda tentativa de ação — permitida, bloqueada ou aguardando confirmação — é
registrada em `.devscope/logs/audit.jsonl` (já coberto pelo `.gitignore` existente,
`.devscope/logs/`), uma linha JSON por evento:

```json
{
  "timestamp": "2026-07-15T12:00:00Z",
  "plugin": "docker",
  "action": "restart_container",
  "kind": "write_reversible",
  "profile": "development",
  "outcome": "executed",
  "project_root": "/caminho/do/projeto",
  "parameters": {"container": "web-1"}
}
```

- `outcome` é um de: `executed`, `blocked`, `awaiting_confirmation`, `confirmed`,
  `expired`.
- `parameters` nunca contém segredos — ver seção seguinte.
- O formato é JSONL desde o primeiro plugin porque é o que o pilar Observability
  (roadmap) vai consumir depois, sem precisar de um redesenho do formato de log.

## Credenciais nunca passam pelo agente

Um plugin nunca recebe usuário, senha, token ou chave como parâmetro de ferramenta
MCP — isso significa que o agente (e o modelo de linguagem por trás dele) nunca vê a
credencial. Cada plugin resolve suas próprias credenciais a partir de variáveis de
ambiente ou de um arquivo de segredos local, referenciado em `devscope.json`:

```json
{
  "plugins": {
    "docker": { "profile": "development" },
    "sentry": { "profile": "read-only", "credentialsEnv": "SENTRY_AUTH_TOKEN" }
  }
}
```

Qualquer valor de configuração cujo nome bata com um padrão de segredo comum
(`token`, `password`, `secret`, `key`, `credential`) é redigido (`"***"`) antes de
entrar na trilha de auditoria, mesmo que apareça por engano em `parameters`.

## Restrição por plugin em `devscope.json`

Um operador pode restringir um plugin individual abaixo do perfil global, nunca
acima dele. Se o perfil global é `development` mas `devscope.json` define
`"docker": {"profile": "read-only"}`, o plugin Docker roda como `read-only`
independente do perfil geral. O inverso — um plugin mais permissivo que o perfil
global — não é uma configuração válida.

## Checklist antes de aceitar o primeiro plugin (ChatGuru)

- [ ] Toda ação do plugin está listada com seu `kind` (`read` / `write_reversible` /
      `write_destructive`) em um manifesto, não descoberta por inspeção do código.
- [ ] Nenhuma ação `write_destructive` executa sem passar pelo protocolo de duas
      etapas (`confirmation_token` + `confirm_action`).
- [ ] Toda tentativa de ação grava uma linha em `.devscope/logs/audit.jsonl`.
- [ ] Nenhuma credencial é aceita como parâmetro de ferramenta MCP.
- [ ] O plugin respeita restrição por-plugin em `devscope.json`, não só o perfil
      global.
