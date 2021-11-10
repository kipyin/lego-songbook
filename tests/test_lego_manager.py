"""Tests for `legoworship` module."""
from typing import Generator

import pytest

import legoworship


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield legoworship.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "2021.11.0"
