from __future__ import annotations

from pathlib import Path
from typing import Literal

from langchain_core.tools import tool


@tool
def code_editor(
    action: Literal["read", "write", "str_replace", "list_dir"],
    path: str,
    content: str = "",
    old_str: str = "",
    new_str: str = "",
) -> str:
    """Read, write, or edit files — the primary tool for working with code.

    Actions:
      read       — return the file's contents with line numbers
      write      — overwrite (or create) a file with `content`
      str_replace — replace the first occurrence of `old_str` with `new_str` in the file
      list_dir   — list files and subdirectories at `path`

    Args:
        action: One of read / write / str_replace / list_dir
        path: File or directory path (absolute or relative)
        content: New file content (write only)
        old_str: Text to find (str_replace only)
        new_str: Replacement text (str_replace only)
    """
    p = Path(path)
    try:
        if action == "read":
            if not p.exists():
                return f"Error: {path} not found"
            lines = p.read_text(errors="replace").splitlines()
            return "\n".join(f"{i + 1:4}: {line}" for i, line in enumerate(lines))

        if action == "write":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return f"Wrote {len(content)} characters to {path}"

        if action == "str_replace":
            if not p.exists():
                return f"Error: {path} not found"
            text = p.read_text()
            if old_str not in text:
                return f"Error: string not found in {path}"
            p.write_text(text.replace(old_str, new_str, 1))
            return f"Replaced in {path}"

        if action == "list_dir":
            if not p.exists():
                return f"Error: {path} not found"
            entries = sorted(p.iterdir(), key=lambda e: (e.is_file(), e.name))
            return "\n".join(
                f"{'d' if e.is_dir() else 'f'}  {e.name}" for e in entries
            )

        return f"Error: unknown action '{action}'"
    except Exception as e:
        return f"Error: {e}"
