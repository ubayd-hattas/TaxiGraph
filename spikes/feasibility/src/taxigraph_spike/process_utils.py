"""Subprocess helpers shared by the validator/OTP wrappers.

Only the spike's own child processes are started or torn down here. Windows
needs the hidden-window creation flag so a background OTP server does not
pop up a console window during automated runs.
"""

from __future__ import annotations

import subprocess
import sys


def _creation_flags() -> int:
    if sys.platform == "win32":
        return subprocess.CREATE_NO_WINDOW
    return 0


def run_hidden(args: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=_creation_flags(),
    )


def popen_hidden(args: list[str]) -> subprocess.Popen:
    return subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=_creation_flags(),
    )
