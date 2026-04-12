from __future__ import annotations

import subprocess

from langchain_core.tools import tool

# Patterns too dangerous to allow regardless of intent
_BLOCKED = [
    "rm -rf /",
    "rm -rf ~",
    "mkfs",
    "> /dev/sd",
    ":(){ :|:& };:",
    "dd if=/dev/zero",
]


@tool
def bash_exec(command: str, timeout: int = 30, working_dir: str = ".") -> str:
    """Execute a bash shell command and return its output (stdout + stderr).

    Args:
        command: The shell command to run.
        timeout: Max seconds to wait before killing the process (default 30).
        working_dir: Directory to run the command in (default current dir).

    Commands run with your user's permissions — use with care.
    """
    for blocked in _BLOCKED:
        if blocked in command:
            return f"Error: blocked command pattern — '{blocked}'"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir,
        )
        output = result.stdout
        if result.stderr:
            output += ("\n[stderr]\n" if result.stdout else "") + result.stderr
        return output.rstrip() or f"(exit code {result.returncode}, no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"
