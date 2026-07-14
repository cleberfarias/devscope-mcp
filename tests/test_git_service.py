import subprocess
from pathlib import Path

from devscope.services.git_service import GitService


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_analyzes_current_branch(tmp_path: Path) -> None:
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "README.md").write_text("initial\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "initial")
    git(tmp_path, "checkout", "-b", "feature/test")
    (tmp_path / "feature.py").write_text("value = 1\n", encoding="utf-8")
    git(tmp_path, "add", "feature.py")
    git(tmp_path, "commit", "-m", "add feature")

    result = GitService(tmp_path).analyze("main")

    assert result.branch == "feature/test"
    assert result.ahead == 1
    assert result.behind == 0
    assert result.working_tree_clean is True
    assert result.changed_files[0].path == "feature.py"
