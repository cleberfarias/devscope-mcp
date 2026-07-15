import re

_STOPWORDS = {
    # português — verbos/termos genéricos de tarefa, sem sinal específico de código
    "sistema", "sistemas", "aplicação", "aplicacao", "processo", "processos",
    "informação", "informacao", "usuário", "usuario", "usuários", "usuarios",
    "porque", "também", "tambem", "sobre", "quando", "sempre", "deve", "devem",
    "implementar", "corrigir", "problema", "criar", "adicionar", "verificar",
    "garantir", "atualizar", "melhorar", "realizar", "necessário", "necessario",
    # inglês — mesma categoria
    "should", "would", "could", "about", "which", "there", "their", "these",
    "those", "where", "system", "process", "application", "please", "implement",
    "create", "update", "ensure", "verify", "improve", "handle", "provide",
}

_WORD_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)


def extract_keywords(task: str, limit: int = 8) -> list[str]:
    """Extrai termos de busca de uma descrição de tarefa em linguagem natural.

    Ignora pontuação, palavras curtas (menos de 5 letras) e uma lista pequena de
    palavras genéricas de tarefa que não ajudam a localizar código (ex.:
    "implementar", "sistema"). Preserva a grafia original do termo — importante
    para identificadores como `UserService` — mas deduplica sem diferenciar
    maiúsculas de minúsculas.
    """
    seen: set[str] = set()
    terms: list[str] = []
    for match in _WORD_PATTERN.finditer(task):
        word = match.group()
        lowered = word.lower()
        if len(word) < 5 or lowered in _STOPWORDS or lowered in seen:
            continue
        seen.add(lowered)
        terms.append(word)
        if len(terms) >= limit:
            break
    return terms
