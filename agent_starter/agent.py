from __future__ import annotations

import uuid
from typing import AsyncIterator, Callable

from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from .config import AgentConfig, load_config
from .graph import build_graph


class AgentKit:
    """Main entry point. Clone the repo and customize from here."""

    def __init__(
        self,
        agent_name: str = "default",
        config_dir: str = "agents",
        config: AgentConfig | None = None,
    ) -> None:
        self.config = config or load_config(agent_name, config_dir)
        self._extra_tools: list[BaseTool] = []
        self._graph = None  # built lazily on first use

    def _get_graph(self):
        if self._graph is None:
            self._graph = build_graph(self.config, self._extra_tools)
        return self._graph

    def tool(self, func: Callable) -> Callable:
        """Decorator to add a custom tool. Must be called before first chat()."""
        from langchain_core.tools import tool as lc_tool
        t = lc_tool(func)
        self._extra_tools.append(t)
        self._graph = None  # force rebuild
        return func

    def add_tool(self, t: BaseTool) -> None:
        """Add a pre-built LangChain tool."""
        self._extra_tools.append(t)
        self._graph = None

    def chat(
        self,
        message: str,
        thread_id: str = "default",
        user_id: str = "default",
    ) -> str:
        """Send a message and return the full response string."""
        graph = self._get_graph()
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        state_input = {
            "messages": [HumanMessage(content=message)],
            "memory_context": "",
            "user_profile": {"user_id": user_id},
        }
        result = graph.invoke(state_input, config=config)
        return result["messages"][-1].content

    async def stream(
        self,
        message: str,
        thread_id: str = "default",
        user_id: str = "default",
    ) -> AsyncIterator[str]:
        """Stream response tokens as they arrive."""
        graph = self._get_graph()
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        state_input = {
            "messages": [HumanMessage(content=message)],
            "memory_context": "",
            "user_profile": {"user_id": user_id},
        }
        async for event in graph.astream_events(state_input, config=config, version="v2"):
            if (
                event["event"] == "on_chat_model_stream"
                and event["metadata"].get("langgraph_node") == "agent"
            ):
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield chunk.content

    def serve(self, host: str | None = None, port: int | None = None) -> None:
        """Start the FastAPI server."""
        from .server import run_server
        run_server(
            self,
            host=host or self.config.server_host,
            port=port or self.config.server_port,
        )

    def new_thread(self) -> str:
        """Generate a unique thread ID for a new conversation."""
        return str(uuid.uuid4())
