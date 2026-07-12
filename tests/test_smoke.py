"""Smoke test — ensure the project imports cleanly."""

from src.main import repl, demo


def test_repl_imports():
    """repl function exists and is callable."""
    assert callable(repl)


def test_demo_imports():
    """demo function exists and is callable."""
    assert callable(demo)