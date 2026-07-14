from pathlib import Path

from devscope.models.config import DevScopeConfig
from devscope.services.code_search import CodeSearch


def test_search_finds_line(tmp_path: Path) -> None:
    source = tmp_path / "service.py"
    source.write_text("def health_check():\n    return 'ok'\n", encoding="utf-8")

    result = CodeSearch(tmp_path, DevScopeConfig()).search("health_check")

    assert len(result.matches) == 1
    assert result.matches[0].file == "service.py"
    assert result.matches[0].line == 1
