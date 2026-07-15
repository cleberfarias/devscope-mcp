from pathlib import Path

import pytest

from devscope.security.paths import PathSecurityError, resolve_inside_root, resolve_project_root


def test_resolve_project_root(tmp_path: Path) -> None:
    assert resolve_project_root(tmp_path) == tmp_path.resolve()


def test_blocks_path_outside_root(tmp_path: Path) -> None:
    with pytest.raises(PathSecurityError):
        resolve_inside_root(tmp_path, "../outside.txt")
