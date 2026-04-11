"""
Example 3 — Multi-Agent Supervisor + Long-Term Memory + API Server
===================================================================
A supervisor agent delegates to a research sub-agent.
Long-term memory persists user facts across sessions.
The system is also served via FastAPI.

Architecture:
  User → Supervisor → [research_agent] → Response
                    → [direct answer]  → Response

Run:
  python examples/03_advanced/run.py

Then in another terminal:
  curl -X POST http://localhost:8000/chat \\
    -H "Content-Type: application/json" \\
    -d '{"message": "What are the latest AI news?", "user_id": "alice"}'
"""
from __future__ import annotations

import asyncio

from langchain_core.tools import tool

from agent_starter import AgentKit
from agent_starter.config import AgentConfig

# ── Sub-agent: specialised researcher ────────────────────────────────────────
research_config = AgentConfig(
    name="researcher",
    persona_text=(
        "You are a precise research assistant. When given a topic, provide a "
        "thorough, well-structured summary with key facts and figures. "
        "Always indicate the date of your knowledge."
    ),
    tools=["web_search", "calculator"],
)
researcher = AgentKit(config=research_config)


# ── Supervisor: routes tasks to the researcher ────────────────────────────────
supervisor = AgentKit()


@supervisor.tool
def delegate_research(topic: str) -> str:
    """Delegate a research task to the specialised research agent."""
    print(f"  [supervisor → researcher]: {topic}")
    return researcher.chat(topic, thread_id="research-thread", user_id="supervisor")


# ── Async streaming demo ──────────────────────────────────────────────────────
async def streaming_demo():
    print("\n── Streaming demo ───────────────────────────────────────────")
    print("Agent: ", end="", flush=True)
    async for token in supervisor.stream(
        "Tell me briefly why LangGraph is good for building agents.",
        thread_id="stream-demo",
    ):
        print(token, end="", flush=True)
    print("\n")


# ── Interactive chat with long-term memory ────────────────────────────────────
def interactive_demo():
    USER_ID = "alice"
    THREAD_ID = "advanced-demo"

    print("\n── Multi-agent chat (long-term memory enabled) ──────────────")
    print("Your preferences and facts will be remembered across sessions.")
    print("Try: 'Research the latest on LangGraph' or 'What is 2^32?'\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in {"exit", "quit"}:
            break
        response = supervisor.chat(user_input, thread_id=THREAD_ID, user_id=USER_ID)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    import sys

    if "--serve" in sys.argv:
        # Start API server
        supervisor.serve(port=8000)
    elif "--stream" in sys.argv:
        asyncio.run(streaming_demo())
    else:
        interactive_demo()
