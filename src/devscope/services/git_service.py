import subprocess
from pathlib import Path

from devscope.models.responses import BranchAnalysisResult, ChangedFile, CommitInfo


class GitService:
    ALLOWED_COMMANDS = {
        "branch", "status", "diff", "log", "rev-list", "rev-parse", "show-ref"
    }

    def __init__(self, root: Path) -> None:
        self.root = root

    def analyze(self, base_branch: str) -> BranchAnalysisResult:
        if not (self.root / ".git").exists():
            raise ValueError(f"O diretório não é um repositório Git: {self.root}")

        branch = self._run("branch", "--show-current").strip() or "HEAD destacado"
        status_lines = self._run("status", "--porcelain").splitlines()
        warnings: list[str] = []

        base_ref = self._resolve_base(base_branch)
        if base_ref is None:
            warnings.append(f"Branch base não encontrada: {base_branch}")
            base_ref = base_branch
            ahead = behind = 0
            changed: list[ChangedFile] = []
            commits: list[CommitInfo] = []
        else:
            counts = self._run("rev-list", "--left-right", "--count", f"{base_ref}...HEAD").split()
            behind, ahead = (int(counts[0]), int(counts[1])) if len(counts) == 2 else (0, 0)
            changed = self._parse_changed(self._run("diff", "--name-status", f"{base_ref}...HEAD"))
            commits = self._parse_commits(self._run("log", "--format=%h%x09%s", f"{base_ref}..HEAD"))

        if behind > 0:
            warnings.append(f"A branch está {behind} commit(s) atrás de {base_ref}.")
        if status_lines:
            warnings.append("Existem alterações locais ainda não commitadas.")

        return BranchAnalysisResult(
            branch=branch,
            base_branch=base_ref,
            ahead=ahead,
            behind=behind,
            working_tree_clean=not status_lines,
            changed_files=changed,
            commits=commits,
            warnings=warnings,
        )

    def _resolve_base(self, base: str) -> str | None:
        candidates = [base, f"origin/{base}"]
        for candidate in candidates:
            result = subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{candidate}"],
                cwd=self.root,
                check=False,
            )
            if result.returncode == 0:
                return candidate
            remote_ref = f"refs/remotes/{candidate}"
            result = subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", remote_ref],
                cwd=self.root,
                check=False,
            )
            if result.returncode == 0:
                return candidate
        return None

    def _run(self, command: str, *args: str) -> str:
        if command not in self.ALLOWED_COMMANDS:
            raise ValueError(f"Comando Git bloqueado: {command}")
        process = subprocess.run(
            ["git", command, *args], cwd=self.root, capture_output=True,
            text=True, timeout=20, check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(process.stderr.strip() or f"Falha ao executar git {command}")
        return process.stdout

    @staticmethod
    def _parse_changed(output: str) -> list[ChangedFile]:
        items: list[ChangedFile] = []
        for line in output.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                items.append(ChangedFile(status=parts[0], path=parts[-1]))
        return items

    @staticmethod
    def _parse_commits(output: str) -> list[CommitInfo]:
        items: list[CommitInfo] = []
        for line in output.splitlines():
            hash_value, separator, message = line.partition("\t")
            if separator:
                items.append(CommitInfo(hash=hash_value, message=message))
        return items
