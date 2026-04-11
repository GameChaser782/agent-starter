"""agent-starter — A local-first LangGraph agent framework."""

from .agent import AgentKit
from .config import AgentConfig, load_config

__version__ = "0.1.0"
__all__ = ["AgentKit", "AgentConfig", "load_config"]
