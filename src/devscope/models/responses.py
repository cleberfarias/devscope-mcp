from pydantic import BaseModel, Field


class Evidence(BaseModel):
    file: str
    reason: str
    line: int | None = None
    excerpt: str | None = None


class ChangedFile(BaseModel):
    path: str
    status: str


class CommitInfo(BaseModel):
    hash: str
    message: str


class ProjectScanResult(BaseModel):
    project_name: str
    project_root: str
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    package_managers: list[str] = Field(default_factory=list)
    test_frameworks: list[str] = Field(default_factory=list)
    infrastructure: list[str] = Field(default_factory=list)
    important_files: list[str] = Field(default_factory=list)
    confidence: str = "medium"
    evidence: list[Evidence] = Field(default_factory=list)


class BranchAnalysisResult(BaseModel):
    branch: str
    base_branch: str
    ahead: int = 0
    behind: int = 0
    working_tree_clean: bool
    changed_files: list[ChangedFile] = Field(default_factory=list)
    commits: list[CommitInfo] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class SearchMatch(BaseModel):
    file: str
    line: int
    excerpt: str


class SearchResult(BaseModel):
    query: str
    matches: list[SearchMatch] = Field(default_factory=list)
    truncated: bool = False
