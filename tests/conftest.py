"""Pytest configuration — isolates session files for testing."""

import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _isolate_session(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Give each test a unique, clean session so tests don't share state."""
    # Use the full nodeid (includes file path + test name) to avoid collisions
    nodeid = request.node.nodeid.replace("/", "_").replace("::", "_").replace(".py", "")
    monkeypatch.setenv("BARENODE_SESSION", f"test_{nodeid}")

    # Use a temporary directory for session files so they don't persist
    # between test runs
    tmp_session_dir = tempfile.mkdtemp(prefix="barenode_test_sessions_")
    monkeypatch.setenv("BARENODE_SESSION_DIR", tmp_session_dir)

    # Clean up the temp directory after the test
    def _cleanup():
        import shutil
        if os.path.isdir(tmp_session_dir):
            shutil.rmtree(tmp_session_dir)
    request.addfinalizer(_cleanup)