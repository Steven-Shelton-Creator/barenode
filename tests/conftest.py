"""Pytest configuration — isolates session files for testing."""

import pytest


@pytest.fixture(autouse=True)
def _isolate_session(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Give each test a unique session name so tests don't share state."""
    # Use the full nodeid (includes file path + test name) to avoid collisions
    nodeid = request.node.nodeid.replace("/", "_").replace("::", "_").replace(".py", "")
    monkeypatch.setenv("BARENODE_SESSION", f"test_{nodeid}")