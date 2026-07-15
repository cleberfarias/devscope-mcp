import pytest

from devscope_auth.authorize import Decision, authorize
from devscope_auth.manifest import ActionKind, ActionManifest

READ = ActionManifest(name="read_thing", kind=ActionKind.READ)
WRITE_REVERSIBLE = ActionManifest(name="restart_thing", kind=ActionKind.WRITE_REVERSIBLE)
WRITE_REVERSIBLE_REVIEW = ActionManifest(
    name="comment_pr", kind=ActionKind.WRITE_REVERSIBLE, scope="review"
)
WRITE_DESTRUCTIVE = ActionManifest(name="delete_thing", kind=ActionKind.WRITE_DESTRUCTIVE)


@pytest.mark.parametrize("profile", ["read-only", "development", "review"])
def test_read_always_allowed(profile: str) -> None:
    assert authorize(profile, READ) is Decision.ALLOWED


def test_read_only_blocks_reversible_write() -> None:
    assert authorize("read-only", WRITE_REVERSIBLE) is Decision.BLOCKED


def test_read_only_blocks_destructive_write() -> None:
    assert authorize("read-only", WRITE_DESTRUCTIVE) is Decision.BLOCKED


def test_development_allows_reversible_without_confirmation() -> None:
    assert authorize("development", WRITE_REVERSIBLE) is Decision.ALLOWED


def test_development_requires_confirmation_for_destructive() -> None:
    assert authorize("development", WRITE_DESTRUCTIVE) is Decision.NEEDS_CONFIRMATION


def test_review_blocks_destructive_even_though_development_would_confirm() -> None:
    assert authorize("review", WRITE_DESTRUCTIVE) is Decision.BLOCKED


def test_review_blocks_reversible_outside_review_scope() -> None:
    assert authorize("review", WRITE_REVERSIBLE) is Decision.BLOCKED


def test_review_allows_reversible_within_review_scope() -> None:
    assert authorize("review", WRITE_REVERSIBLE_REVIEW) is Decision.ALLOWED


def test_unknown_profile_raises() -> None:
    with pytest.raises(ValueError):
        authorize("nonexistent", READ)
