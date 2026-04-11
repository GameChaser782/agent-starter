"""
Example 1 — Basic Agent
=======================
The simplest possible agent. Loads default config, chats, done.

Prerequisites:
  1. ollama serve
  2. ollama pull llama3.2
  3. pip install -e .        (from repo root)

Run:
  python examples/01_basic/run.py
"""
from agent_starter import AgentKit

agent = AgentKit()

print("Agent ready. Type 'exit' to quit.\n")
thread = agent.new_thread()

while True:
    user_input = input("You: ").strip()
    if not user_input or user_input.lower() in {"exit", "quit"}:
        break
    response = agent.chat(user_input, thread_id=thread)
    print(f"Agent: {response}\n")
