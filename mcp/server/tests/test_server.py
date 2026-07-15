import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

from devscope import server
from devscope.config import load_config
from devscope.context import AppContext
from devscope.security.paths import PathSecurityError
from devscope.services.project_scanner import ProjectScanner


@pytest.fixture(autouse=True)
def _reset_app() -> Iterator[None]:
    server._scan_cache.clear()
    yield
    server._app = None
    server._scan_cache.clear()


def _init_app(tmp_path: Path) -> None:
    config = load_config(tmp_path)
    server._app = AppContext(project_root=tmp_path, config=config)


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "README.md").write_text("hi\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=root, check=True)


def test_health_check_requires_initialized_app() -> None:
    with pytest.raises(RuntimeError):
        server.health_check()


def test_health_check_reports_active_project(tmp_path: Path) -> None:
    _init_app(tmp_path)

    result = server.health_check()

    assert result["status"] == "ok"
    assert result["project_root"] == str(tmp_path)
    assert result["security_profile"] == "read-only"


def test_scan_project_detects_python_manifest(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("print('hi')\n", encoding="utf-8")
    _init_app(tmp_path)

    result = server.scan_project()

    assert "Python" in result["languages"]
    assert "pyproject.toml" in result["important_files"]


def test_scan_project_reuses_cache_within_ttl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "main.py").write_text("print('hi')\n", encoding="utf-8")
    _init_app(tmp_path)
    calls = 0
    original_scan = ProjectScanner.scan

    def counting_scan(self: ProjectScanner) -> object:
        nonlocal calls
        calls += 1
        return original_scan(self)

    monkeypatch.setattr(ProjectScanner, "scan", counting_scan)

    first = server.scan_project()
    second = server.scan_project()

    assert first == second
    assert calls == 1


def test_analyze_current_branch_requires_git_repo(tmp_path: Path) -> None:
    _init_app(tmp_path)

    with pytest.raises(ValueError):
        server.analyze_current_branch()


def test_analyze_current_branch_reports_clean_tree(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    _init_app(tmp_path)

    result = server.analyze_current_branch(base_branch="main")

    assert result["branch"] == "main"
    assert result["working_tree_clean"] is True
    assert result["ahead"] == 0
    assert result["behind"] == 0


def test_search_code_context_finds_match(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("def handler():\n    pass\n", encoding="utf-8")
    _init_app(tmp_path)

    result = server.search_code_context("handler")

    assert result["matches"][0]["file"] == "app.py"
    assert result["matches"][0]["line"] == 1


def test_search_code_context_blocks_path_outside_root(tmp_path: Path) -> None:
    _init_app(tmp_path)

    with pytest.raises(PathSecurityError):
        server.search_code_context("handler", path="../outside")


def test_get_task_context_warns_when_agents_file_missing(tmp_path: Path) -> None:
    _init_app(tmp_path)

    result = server.get_task_context("investigar login expirado")

    assert result["instructions"] is None
    assert any("AGENTS.md" in warning for warning in result["warnings"])


def test_get_task_context_includes_instructions_when_present(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# regras do projeto\n", encoding="utf-8")
    _init_app(tmp_path)

    result = server.get_task_context("qualquer tarefa")

    assert result["instructions"]["file"] == "AGENTS.md"
    assert "regras do projeto" in result["instructions"]["content"]
