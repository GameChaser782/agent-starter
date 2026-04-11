from pathlib import Path

from langchain_core.tools import tool


@tool
def file_reader(path: str) -> str:
    """Read a local text file and return its contents. Provide an absolute or relative path."""
    try:
        p = Path(path)
        if not p.exists():
            return f"Error: file not found — {path}"
        if p.stat().st_size > 1_000_000:
            return f"Error: file too large (>{1_000_000} bytes) — {path}"
        return p.read_text(errors="replace")
    except Exception as e:
        return f"Error reading file: {e}"
