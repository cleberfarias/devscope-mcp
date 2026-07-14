# Arquitetura inicial

```text
VS Code / agente MCP
        |
        | stdio / JSON-RPC
        v
   DevScope server
        |
        +-- ProjectScanner
        +-- GitService
        +-- CodeSearch
        +-- Config + Path Security
        |
        v
Projeto local (somente leitura)
```

O servidor não aceita comandos shell arbitrários. Cada capacidade é exposta por uma ferramenta específica e limitada.
