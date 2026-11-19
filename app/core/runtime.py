"""Runtime guard: the project is pinned to Python 3.12 on the VM.

The system ``python3`` is 3.6.8 (EOL); using it accidentally would silently
break FastAPI / Pydantic v2. Fail fast instead of guessing.
"""
import platform
import sys

SUPPORTED_PYTHON = (3, 12)


def assert_supported_runtime() -> None:
    if sys.version_info[:2] != SUPPORTED_PYTHON:
        raise RuntimeError(
            "Childhood Library API requires Python 3.12, got "
            f"{platform.python_version()} ({sys.executable}). "
            "Use the repo .venv (python3.12 -m venv .venv)."
        )


def python_version() -> str:
    return platform.python_version()
