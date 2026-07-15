import pytest

from devscope_plugin_chatguru.security import InvalidBaseUrlError, validate_base_url


def test_accepts_valid_https_public_host() -> None:
    validate_base_url("https://api.chatguru.exemplo.com")


def test_rejects_non_https_scheme() -> None:
    with pytest.raises(InvalidBaseUrlError):
        validate_base_url("http://api.chatguru.exemplo.com")


def test_rejects_localhost() -> None:
    with pytest.raises(InvalidBaseUrlError):
        validate_base_url("https://localhost")


def test_rejects_loopback_ip() -> None:
    with pytest.raises(InvalidBaseUrlError):
        validate_base_url("https://127.0.0.1")


def test_rejects_private_ip() -> None:
    with pytest.raises(InvalidBaseUrlError):
        validate_base_url("https://10.0.0.5")


def test_rejects_link_local_metadata_ip() -> None:
    with pytest.raises(InvalidBaseUrlError):
        validate_base_url("https://169.254.169.254")


def test_rejects_internal_suffix_host() -> None:
    with pytest.raises(InvalidBaseUrlError):
        validate_base_url("https://metadata.google.internal")


def test_rejects_missing_host() -> None:
    with pytest.raises(InvalidBaseUrlError):
        validate_base_url("https://")
