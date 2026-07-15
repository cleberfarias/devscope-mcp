---
name: git
description: Interpretar o resultado de analyze_current_branch do mcp/server e decidir quando uma branch está pronta para PR.
---

# Skill: Git

Consultada sempre que o agente precisa avaliar o estado de uma branch antes de
continuar uma tarefa ou abrir um Pull Request. Assume que o contexto vem da
ferramenta `analyze_current_branch` do `mcp/server`, que retorna:

```text
branch, base_branch, ahead, behind, working_tree_clean,
changed_files[{path, status}], commits[{hash, message}], warnings[]
```

## Regras de decisão

1. **`working_tree_clean == false`** — há alterações não commitadas. Não abra PR nem
   compare impacto até isso ser resolvido; pergunte ao usuário se quer commitar,
   descartar ou continuar mesmo assim. Nunca descarte automaticamente.

2. **`behind > 0`** — a branch está atrás de `base_branch`. Trate como risco antes de
   qualquer análise de impacto: um diff calculado contra uma base desatualizada
   subestima o que realmente vai mudar quando a branch for integrada. Recomende
   atualizar a branch antes de prosseguir; não prossiga silenciosamente.

3. **`ahead == 0` e `changed_files` vazio** — não há trabalho para analisar. Não
   invente contexto; informe que não há diferença em relação à base.

4. **`warnings` não vazio** — sempre repita os avisos ao usuário em texto, mesmo que
   a tarefa continue. Um aviso descartado silenciosamente é o tipo de coisa que essa
   ferramenta existe para evitar.

5. **Leitura de `changed_files`** — o campo `status` segue a convenção do
   `git diff --name-status` (`A` adicionado, `M` modificado, `D` deletado, `R*`
   renomeado). Arquivos com status `D` não devem ser tratados como "arquivos
   relacionados à tarefa" para efeito de busca de código — eles não existem mais na
   branch atual.

6. **`commits`** — a mensagem de cada commit é a única evidência de intenção
   disponível nessa ferramenta. Se as mensagens não explicam o "porquê" de uma
   mudança em `changed_files`, não presuma motivo — pergunte ou marque como
   desconhecido, em vez de gerar uma justificativa plausível mas não verificada.

## Quando não usar

Se o diretório analisado não é um repositório Git, `analyze_current_branch` falha
com uma exceção antes de retornar esses campos — trate isso como ausência de
contexto de Git, não como branch limpa.
