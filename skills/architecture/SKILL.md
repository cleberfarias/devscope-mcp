---
name: architecture
description: Interpretar o resultado de scan_project do mcp/server para descrever a arquitetura de um projeto com o nível de confiança correto.
---

# Skill: Architecture

Consultada quando o agente precisa descrever a arquitetura, stack ou estrutura de um
projeto. Assume que o contexto vem da ferramenta `scan_project` do `mcp/server`, que
retorna:

```text
project_name, project_root, languages[], frameworks[], package_managers[],
test_frameworks[], infrastructure[], important_files[], confidence,
evidence[{file, reason, line?, excerpt?}]
```

## Regras de decisão

1. **Respeite o campo `confidence`.** Ele vale `"high"` só quando há evidência
   concreta (arquivo de manifesto encontrado ou dependência identificada);
   `"medium"` significa que a detecção veio só de extensões de arquivo, sem
   confirmação. Ao relatar `confidence: "medium"`, diga isso explicitamente —
   não apresente frameworks inferidos por extensão como fato consolidado.

2. **Toda afirmação sobre a stack deve citar `evidence`.** Se `scan_project` diz que
   o projeto usa React porque encontrou a dependência em `package.json`, cite o
   arquivo. Se `frameworks` contém algo sem entrada correspondente em `evidence`,
   foi inferido por heurística de extensão — trate com a mesma cautela do item 1.

3. **`important_files` não é a lista de todos os arquivos relevantes**, é uma lista
   fixa de marcadores conhecidos (`pyproject.toml`, `Dockerfile`,
   `.github/workflows` etc.). Ausência de um marcador na lista não prova que aquela
   tecnologia não existe no projeto — só que o scanner não tem heurística para ela
   ainda. Não conclua "este projeto não usa Docker" apenas porque `infrastructure`
   não lista Docker; diga que o scanner não encontrou evidência, o que é diferente.

4. **`package_managers` múltiplos** (ex.: `npm` e `pip` juntos) é sinal de projeto
   poliglota ou monorepo, não de configuração inconsistente. Não sinalize isso como
   problema por padrão.

5. **`languages` vem de extensão de arquivo, não de análise semântica.** Um projeto
   com um único script `.py` de automação dentro de um repositório majoritariamente
   TypeScript vai listar Python também. Ao resumir a stack principal do projeto,
   priorize `frameworks` e `package_managers` (que exigem evidência de manifesto)
   sobre `languages` sozinho.

## Quando não usar

Para decidir se uma mudança específica é segura ou o que ela impacta, use análise de
impacto (roadmap — ainda não implementada), não esta Skill. `scan_project` descreve
o projeto como um todo, não o efeito de uma mudança pontual.
