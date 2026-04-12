from .bash_executor import bash_exec
from .calculator import calculator
from .code_editor import code_editor
from .file_reader import file_reader
from .github import github_get_issue, github_list_issues, github_read_file
from .image_vision import image_vision
from .python_repl import python_repl
from .sqlite_query import sqlite_query
from .web_search import web_search
from ..registry import ToolRegistry

# Register all builtins on import
ToolRegistry.register(bash_exec)
ToolRegistry.register(calculator)
ToolRegistry.register(code_editor)
ToolRegistry.register(file_reader)
ToolRegistry.register(github_read_file)
ToolRegistry.register(github_list_issues)
ToolRegistry.register(github_get_issue)
ToolRegistry.register(image_vision)
ToolRegistry.register(python_repl)
ToolRegistry.register(sqlite_query)
ToolRegistry.register(web_search)

__all__ = [
    "bash_exec",
    "calculator",
    "code_editor",
    "file_reader",
    "github_read_file",
    "github_list_issues",
    "github_get_issue",
    "image_vision",
    "python_repl",
    "sqlite_query",
    "web_search",
]
