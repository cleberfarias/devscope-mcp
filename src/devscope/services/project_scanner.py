import json
from pathlib import Path

from devscope.models.config import DevScopeConfig
from devscope.models.responses import Evidence, ProjectScanResult


LANGUAGE_MARKERS = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript/JSX",
    ".ts": "TypeScript", ".tsx": "TypeScript/TSX", ".vue": "Vue",
    ".java": "Java", ".go": "Go", ".rs": "Rust", ".php": "PHP",
}


class ProjectScanner:
    def __init__(self, root: Path, config: DevScopeConfig) -> None:
        self.root = root
        self.config = config

    def scan(self) -> ProjectScanResult:
        extensions: set[str] = set()
        important_files: list[str] = []
        evidence: list[Evidence] = []
        frameworks: set[str] = set()
        package_managers: set[str] = set()
        tests: set[str] = set()
        infrastructure: set[str] = set()

        markers = [
            "pyproject.toml", "requirements.txt", "package.json", "Dockerfile",
            "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml",
            "AGENTS.md", "README.md", "Makefile", ".github/workflows",
        ]
        for marker in markers:
            if (self.root / marker).exists():
                important_files.append(marker)

        for file in self._iter_files():
            extensions.add(file.suffix.lower())

        package_json = self.root / "package.json"
        if package_json.exists():
            package_managers.add("npm")
            try:
                package = json.loads(package_json.read_text(encoding="utf-8"))
                deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
                for dep, label in {
                    "react": "React", "vue": "Vue", "next": "Next.js",
                    "vite": "Vite", "express": "Express", "@angular/core": "Angular",
                }.items():
                    if dep in deps:
                        frameworks.add(label)
                        evidence.append(Evidence(file="package.json", reason=f"Dependência {dep} encontrada"))
                for dep, label in {"vitest": "Vitest", "jest": "Jest", "playwright": "Playwright"}.items():
                    if dep in deps or f"@{dep}/test" in deps:
                        tests.add(label)
            except (json.JSONDecodeError, OSError):
                pass

        if (self.root / "pyproject.toml").exists() or (self.root / "requirements.txt").exists():
            package_managers.add("pip")
        python_text = self._read_small_files(["pyproject.toml", "requirements.txt"])
        for marker, label in {
            "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
            "pytest": "pytest", "ruff": "Ruff",
        }.items():
            if marker in python_text.lower():
                (tests if label == "pytest" else frameworks).add(label)

        if any((self.root / name).exists() for name in ["Dockerfile", "docker-compose.yml", "compose.yml"]):
            infrastructure.add("Docker")
        if (self.root / ".github/workflows").exists():
            infrastructure.add("GitHub Actions")

        languages = sorted({LANGUAGE_MARKERS[e] for e in extensions if e in LANGUAGE_MARKERS})
        name = self.config.project.name or self.root.name
        confidence = "high" if evidence or important_files else "medium"
        return ProjectScanResult(
            project_name=name,
            project_root=str(self.root),
            languages=languages,
            frameworks=sorted(frameworks),
            package_managers=sorted(package_managers),
            test_frameworks=sorted(tests),
            infrastructure=sorted(infrastructure),
            important_files=sorted(important_files),
            confidence=confidence,
            evidence=evidence[:20],
        )

    def _iter_files(self):
        ignored = set(self.config.ignore)
        for path in self.root.rglob("*"):
            try:
                relative = path.relative_to(self.root)
            except ValueError:
                continue
            if any(part in ignored for part in relative.parts):
                continue
            if path.is_file() and path.stat().st_size <= self.config.max_file_size_kb * 1024:
                yield path

    def _read_small_files(self, names: list[str]) -> str:
        chunks: list[str] = []
        for name in names:
            path = self.root / name
            if path.exists() and path.is_file():
                try:
                    chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
                except OSError:
                    pass
        return "\n".join(chunks)
