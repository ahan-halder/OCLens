"""Placeholder for batch-mode GDB integration tests (Stage H)."""

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(reason="Stage H — requires PoCL + GDB integration environment")
def test_extension_loads_in_batch_mode() -> None:
    assert True
