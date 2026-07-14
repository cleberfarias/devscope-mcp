from dataclasses import dataclass
from pathlib import Path

from devscope.models.config import DevScopeConfig


@dataclass(frozen=True)
class AppContext:
    project_root: Path
    config: DevScopeConfig
