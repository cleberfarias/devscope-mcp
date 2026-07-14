import json
from pathlib import Path

from devscope.models.config import DevScopeConfig
from devscope.services.project_scanner import ProjectScanner


def test_detects_react_vitest_and_docker(tmp_path: Path) -> None:
    package = {
        "dependencies": {"react": "^19.0.0"},
        "devDependencies": {"vitest": "^3.0.0"},
    }
    (tmp_path / "package.json").write_text(json.dumps(package), encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM node:22\n", encoding="utf-8")
    (tmp_path / "src.tsx").write_text("export const App = () => null\n", encoding="utf-8")

    result = ProjectScanner(tmp_path, DevScopeConfig()).scan()

    assert "React" in result.frameworks
    assert "Vitest" in result.test_frameworks
    assert "Docker" in result.infrastructure
    assert "TypeScript/TSX" in result.languages
