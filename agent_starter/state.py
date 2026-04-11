from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State that flows through the agent graph each turn."""

    # Full conversation history — add_messages handles appending correctly
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Injected at the start of each turn from long-term memory
    memory_context: str

    # Accumulated across sessions (name, preferences, etc.)
    user_profile: dict
