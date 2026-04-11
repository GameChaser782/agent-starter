"""
Example 2 — Custom Tools + Persistent Memory
=============================================
Shows how to add a custom tool and use thread memory
so the agent remembers the conversation across turns.

Run:
  python examples/02_intermediate/run.py
"""
from agent_starter import AgentKit

agent = AgentKit()


# ── Add a custom tool with the @agent.tool decorator ─────────────────────────
@agent.tool
def get_weather(city: str) -> str:
    """Get the current weather for a city (stubbed for demo)."""
    # Replace with a real weather API call
    return f"It's 22°C and sunny in {city}. (demo — replace with real API)"


@agent.tool
def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    import os
    try:
        files = os.listdir(directory)
        return "\n".join(files[:20]) or "Empty directory"
    except Exception as e:
        return f"Error: {e}"


# ── Persistent thread — the agent remembers previous turns ───────────────────
THREAD_ID = "demo-session-02"

print("Agent with custom tools ready. The agent will remember this conversation.\n")
print("Try: 'What's the weather in Tokyo?' or 'List the files in .'\n")

while True:
    user_input = input("You: ").strip()
    if not user_input or user_input.lower() in {"exit", "quit"}:
        break
    response = agent.chat(user_input, thread_id=THREAD_ID, user_id="demo-user")
    print(f"Agent: {response}\n")
