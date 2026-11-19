"""Runtime guard: only Python 3.12 is supported on this VM."""
import sys

import pytest

from app.core import runtime


def test_runtime_is_python_312():
    assert sys.version_info[:2] == (3, 12)
    runtime.assert_supported_runtime()
    assert runtime.python_version().startswith("3.12")


def test_non_312_runtime_is_rejected(monkeypatch):
    monkeypatch.setattr(runtime.sys, "version_info", (3, 11, 0, "final", 0))
    with pytest.raises(RuntimeError, match="requires Python 3.12"):
        runtime.assert_supported_runtime()
