from .calculator import calculator
from .file_reader import file_reader
from .web_search import web_search
from ..registry import ToolRegistry

# Register all builtins on import
ToolRegistry.register(calculator)
ToolRegistry.register(file_reader)
ToolRegistry.register(web_search)

__all__ = ["calculator", "file_reader", "web_search"]
