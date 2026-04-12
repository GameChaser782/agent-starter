from __future__ import annotations

import sqlite3
from pathlib import Path

from langchain_core.tools import tool


@tool
def sqlite_query(db_path: str, query: str) -> str:
    """Run a SQL query on a SQLite database and return results as a formatted table.

    Args:
        db_path: Path to the .db file (e.g. "data/app.db")
        query: SQL to execute. SELECT is safe; INSERT/UPDATE/DELETE will commit changes.

    To inspect a database schema, run: SELECT name FROM sqlite_master WHERE type='table';
    """
    try:
        p = Path(db_path)
        if not p.exists():
            return f"Error: database not found — {db_path}"

        conn = sqlite3.connect(str(p))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(query)

        # For non-SELECT queries, commit and report rows affected
        if cursor.description is None:
            conn.commit()
            conn.close()
            return f"OK — {cursor.rowcount} row(s) affected"

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "(query returned no rows)"

        cols = list(rows[0].keys())
        col_widths = {c: len(c) for c in cols}
        for row in rows:
            for c in cols:
                val = row[c]
                col_widths[c] = max(col_widths[c], len(str(val) if val is not None else "NULL"))

        sep = "+-" + "-+-".join("-" * col_widths[c] for c in cols) + "-+"
        header = "| " + " | ".join(c.ljust(col_widths[c]) for c in cols) + " |"

        lines = [sep, header, sep]
        for row in rows:
            cells = " | ".join(
                str(row[c] if row[c] is not None else "NULL").ljust(col_widths[c])
                for c in cols
            )
            lines.append(f"| {cells} |")
        lines.append(sep)
        lines.append(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")
        return "\n".join(lines)

    except sqlite3.Error as e:
        return f"SQL error: {e}"
    except Exception as e:
        return f"Error: {e}"
