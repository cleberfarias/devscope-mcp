import time

from devscope.cache import TTLCache


def test_returns_none_before_first_set() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=10)
    assert cache.get() is None


def test_returns_cached_value_within_ttl() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=10)
    cache.set(42)
    assert cache.get() == 42


def test_expires_after_ttl() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=0.05)
    cache.set(42)
    time.sleep(0.1)
    assert cache.get() is None


def test_clear_forces_recompute() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=10)
    cache.set(42)
    cache.clear()
    assert cache.get() is None
