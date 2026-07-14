import json
from pathlib import Path

from devscope.cli import doctor, init_project, scan_project, upgrade_project


def test_init_creates_cross_platform_project_files(tmp_path: Path) -> None:
    result = init_project(tmp_path, base_branch="development")

    assert result["files"]["devscope.json"] == "created"
    config = json.loads((tmp_path / "devscope.json").read_text())
    mcp = json.loads((tmp_path / ".vscode" / "mcp.json").read_text())

    assert config["schemaVersion"] == 1
    assert config["git"]["baseBranch"] == "development"
    assert mcp["servers"]["devscope"]["command"] == "devscope-mcp"
    assert "${workspaceFolder}" in mcp["servers"]["devscope"]["args"]
    assert (tmp_path / "AGENTS.md").exists()


def test_init_does_not_overwrite_without_force(tmp_path: Path) -> None:
    target = tmp_path / "AGENTS.md"
    target.write_text("custom")
    result = init_project(tmp_path)
    assert result["files"]["AGENTS.md"] == "skipped"
    assert target.read_text() == "custom"


def test_upgrade_adds_schema_version(tmp_path: Path) -> None:
    (tmp_path / "devscope.json").write_text('{"project":{"name":"sample"}}')
    result = upgrade_project(tmp_path)
    data = json.loads((tmp_path / "devscope.json").read_text())
    assert result["status"] == "updated"
    assert data["schemaVersion"] == 1
    assert data["security"]["profile"] == "read-only"


def test_doctor_and_scan(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"dependencies":{"react":"^19"}}')
    init_project(tmp_path)
    diagnosis = doctor(tmp_path)
    scan = scan_project(tmp_path)
    assert diagnosis["ready"] is True
    assert diagnosis["project"]["devscope_config"] is True
    assert "React" in scan["frameworks"]
