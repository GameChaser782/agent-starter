from __future__ import annotations

import subprocess
import sys
import textwrap

from langchain_core.tools import tool


@tool
def python_repl(code: str, timeout: int = 30) -> str:
    """Execute Python code in an isolated subprocess and return the output.

    Args:
        code: Python code to run. Use print() to produce output.
        timeout: Max seconds before the process is killed (default 30).

    Useful for data processing, quick calculations, or testing snippets.
    Imports available: anything installed in the current environment.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(code)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += ("\n[stderr]\n" if result.stdout else "") + result.stderr
        return output.rstrip() or f"(exit code {result.returncode}, no output)"
    except subprocess.TimeoutExpired:
        return f"Error: timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"
