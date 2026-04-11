"""CLI entry point: agent-starter chat / agent-starter serve"""
from __future__ import annotations

import click


@click.group()
@click.version_option("0.1.0", prog_name="agent-starter")
def cli():
    """agent-starter — A local-first LangGraph agent framework."""


@cli.command()
@click.option("--agent", default="default", help="Agent name (matches agents/<name>.yaml)")
@click.option("--config-dir", default="agents", help="Directory containing agent YAML files")
@click.option("--thread", default=None, help="Thread ID (default: new UUID each session)")
@click.option("--user", default="default", help="User ID for long-term memory")
def chat(agent: str, config_dir: str, thread: str | None, user: str):
    """Start an interactive chat session in the terminal."""
    from .agent import AgentKit

    kit = AgentKit(agent_name=agent, config_dir=config_dir)
    thread_id = thread or kit.new_thread()

    print(f"\n  agent-starter  |  {kit.config.name}  |  {kit.config.model_provider}/{kit.config.model_name}")
    print(f"  Thread: {thread_id}  |  Type 'exit' or Ctrl+C to quit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Bye!")
            break

        try:
            response = kit.chat(user_input, thread_id=thread_id, user_id=user)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"[Error] {e}\n")


@cli.command()
@click.option("--agent", default="default", help="Agent name (matches agents/<name>.yaml)")
@click.option("--config-dir", default="agents", help="Directory containing agent YAML files")
@click.option("--host", default=None, help="Bind host (default from config or 0.0.0.0)")
@click.option("--port", default=None, type=int, help="Port (default from config or 8000)")
def serve(agent: str, config_dir: str, host: str | None, port: int | None):
    """Start the FastAPI server."""
    from .agent import AgentKit

    kit = AgentKit(agent_name=agent, config_dir=config_dir)
    kit.serve(host=host, port=port)


if __name__ == "__main__":
    cli()
