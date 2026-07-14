from pathlib import Path

from devscope.models.config import DevScopeConfig
from devscope.models.responses import SearchMatch, SearchResult


class CodeSearch:
    def __init__(self, root: Path, config: DevScopeConfig) -> None:
        self.root = root
        self.config = config

    def search(self, query: str, path: str = ".", max_results: int | None = None) -> SearchResult:
        if not query.strip():
            raise ValueError("A busca não pode ser vazia.")
        limit = min(max_results or self.config.max_search_results, 200)
        start = (self.root / path).resolve()
        try:
            start.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("O caminho de busca deve estar dentro do projeto.") from exc

        matches: list[SearchMatch] = []
        ignored = set(self.config.ignore)
        query_lower = query.lower()
        truncated = False

        files = [start] if start.is_file() else start.rglob("*")
        for file in files:
            if not file.is_file():
                continue
            relative = file.relative_to(self.root)
            if any(part in ignored for part in relative.parts):
                continue
            if file.suffix.lower() not in self.config.allowed_extensions:
                continue
            if file.stat().st_size > self.config.max_file_size_kb * 1024:
                continue
            try:
                for number, line in enumerate(file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if query_lower in line.lower():
                        matches.append(SearchMatch(file=str(relative), line=number, excerpt=line.strip()[:300]))
                        if len(matches) >= limit:
                            truncated = True
                            return SearchResult(query=query, matches=matches, truncated=truncated)
            except OSError:
                continue
        return SearchResult(query=query, matches=matches, truncated=truncated)
