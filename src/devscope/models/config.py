from pathlib import Path

from pydantic import BaseModel, Field


DEFAULT_IGNORES = [
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
]


class ProjectInfo(BaseModel):
    name: str | None = None
    description: str | None = None


class GitConfig(BaseModel):
    base_branch: str = Field(default="development", alias="baseBranch")
    remote: str = "origin"


class ProjectPaths(BaseModel):
    frontend: list[str] = Field(default_factory=list)
    backend: list[str] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=lambda: ["tests"])
    documentation: list[str] = Field(default_factory=lambda: ["docs"])


class SecurityConfig(BaseModel):
    profile: str = "read-only"


class InstructionConfig(BaseModel):
    agents_file: str = Field(default="AGENTS.md", alias="agentsFile")


class DevScopeConfig(BaseModel):
    schema_version: int = Field(default=1, alias="schemaVersion")
    project: ProjectInfo = Field(default_factory=ProjectInfo)
    git: GitConfig = Field(default_factory=GitConfig)
    paths: ProjectPaths = Field(default_factory=ProjectPaths)
    ignore: list[str] = Field(default_factory=lambda: DEFAULT_IGNORES.copy())
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    instructions: InstructionConfig = Field(default_factory=InstructionConfig)
    allowed_extensions: list[str] = Field(
        default_factory=lambda: [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".html", ".css",
            ".scss", ".json", ".md", ".toml", ".yml", ".yaml", ".sh",
        ]
    )
    max_file_size_kb: int = 512
    max_search_results: int = 50


class RuntimeSettings(BaseModel):
    project_root: Path
    config_path: Path | None = None
