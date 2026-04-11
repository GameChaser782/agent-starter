# agent-starter

**A local-first LangGraph agent framework. Clone it, customize it, ship it.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`agent-starter` is a batteries-included starting point for building LangGraph agents. It runs locally with [Ollama](https://ollama.com/) by default — no API keys, no cost, no cloud required.

> **Goal**: Give developers a clean, opinionated base they can clone and have a working agent in under 60 seconds — then extend into something production-ready.

---

## Why another agent template?

Most LangGraph templates are either too minimal (just a graph, no memory, no tooling) or too opinionated (locked into one LLM, one deployment pattern). This template hits the middle:

| Feature | agent-starter |
|---------|--------------|
| Local-first (Ollama default) | ✅ |
| Declarative agent definitions (YAML + markdown) | ✅ |
| Long-term memory across sessions | ✅ |
| Multi-provider LLM support | ✅ |
| Built-in tools + easy custom tools | ✅ |
| FastAPI server + CLI | ✅ |
| Progressive examples (basic → advanced) | ✅ |
| Docker ready | ✅ |

---

## Get started in 60 seconds

```bash
# 1. Clone
git clone https://github.com/GameChaser782/agent-starter.git
cd agent-starter

# 2. Install
pip install -e .

# 3. Start Ollama (if not already running)
ollama serve &
ollama pull llama3.2

# 4. Run
python examples/01_basic/run.py
```

Or use the CLI:

```bash
agent-starter chat
```

---

## How it works

```
You ──► recall_memory ──► agent ──► [tool calls?]
                                         │
                             tools ◄─────┘
                               │
                               ▼
                         agent (with tool results)
                               │
                               ▼
                        extract_memory ──► Response
```

Every turn:
1. **recall_memory** — fetches relevant facts from long-term memory and injects them as context
2. **agent** — calls the LLM with your persona + memory context + tool bindings
3. **tools** — executes any tool calls the agent made (calculator, web search, etc.)
4. **extract_memory** — silently extracts memorable facts from the conversation for next time

---

## Define your agent

Agents are defined with a YAML config + a markdown persona file. No Python needed to customize behavior.

**`agents/my_agent.yaml`**
```yaml
name: my_agent
persona: my_agent_persona.md

model:
  provider: ollama      # ollama | anthropic | openai | google
  name: llama3.2

tools:
  - calculator
  - web_search          # set TAVILY_API_KEY for best results

memory:
  long_term: true
```

**`agents/my_agent_persona.md`**
```markdown
# My Agent

You are a focused coding assistant. You help developers debug Python code.

## Behaviour
- Always ask for a minimal reproducible example
- Suggest fixes with explanations
- Prefer the standard library over third-party packages when possible
```

Then run it:
```bash
agent-starter chat --agent my_agent
```

---

## Add custom tools

```python
from agent_starter import AgentKit

agent = AgentKit()

@agent.tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker symbol."""
    # your implementation here
    return f"${ticker}: $150.00"

response = agent.chat("What's Apple's stock price?")
print(response)
```

---

## LLM providers

The default is Ollama (local, free). Switch providers by setting env vars or updating your agent YAML:

```bash
# Anthropic Claude
pip install 'agent-starter[anthropic]'
export AGENT_PROVIDER=anthropic
export AGENT_MODEL=claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
pip install 'agent-starter[openai]'
export AGENT_PROVIDER=openai
export AGENT_MODEL=gpt-4o
export OPENAI_API_KEY=sk-...
```

---

## Memory system

### Short-term (thread memory)
Built on LangGraph's checkpointing. The agent remembers the full conversation within a thread.

```python
# Same thread_id = agent remembers the conversation
agent.chat("My name is Alice", thread_id="session-1")
agent.chat("What's my name?", thread_id="session-1")  # → "Your name is Alice"
```

### Long-term (cross-session)
Facts about users are extracted automatically and stored in SQLite. They're recalled on future sessions.

```python
# Session 1
agent.chat("I'm a Python developer working on a FastAPI project", user_id="alice")

# Session 2 (different day, different thread)
agent.chat("Can you help me?", user_id="alice")
# Agent: "Of course! Last time we talked about your FastAPI project — where did you leave off?"
```

View stored memories:
```bash
curl http://localhost:8000/memory/alice
```

---

## API server

```bash
agent-starter serve
# → http://localhost:8000
# → http://localhost:8000/docs (interactive API docs)
```

```bash
# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "thread_id": "t1", "user_id": "alice"}'

# Streaming endpoint (SSE)
curl -X POST http://localhost:8000/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a story", "thread_id": "t1"}'
```

---

## Progressive examples

| Example | What it shows |
|---------|--------------|
| [`examples/01_basic/`](examples/01_basic/run.py) | Minimal working agent — 15 lines |
| [`examples/02_intermediate/`](examples/02_intermediate/run.py) | Custom tools + persistent thread memory |
| [`examples/03_advanced/`](examples/03_advanced/run.py) | Multi-agent (supervisor + sub-agent) + long-term memory + streaming |

---

## Example agents

Pre-built agent configurations in [`agents/examples/`](agents/examples/):

- **research_assistant** — web search + synthesis + citations
- **customer_support** — long-term memory of each customer, empathetic tone

```bash
agent-starter chat --agent examples/research_assistant
```

---

## Docker

```bash
docker compose up
```

Set API keys in `.env` (copy from `.env.example`):
```bash
cp .env.example .env
# edit .env with your keys
```

---

## Configuration reference

All YAML keys can be overridden with environment variables:

| YAML key | Env var | Default |
|----------|---------|---------|
| `model.provider` | `AGENT_PROVIDER` | `ollama` |
| `model.name` | `AGENT_MODEL` | `llama3.2` |
| `model.temperature` | `AGENT_TEMPERATURE` | `0.7` |
| `memory.long_term` | `AGENT_LONG_TERM_MEMORY` | `true` |
| `memory.dir` | `AGENT_MEMORY_DIR` | `.agentkit` |
| `server.host` | `AGENT_SERVER_HOST` | `0.0.0.0` |
| `server.port` | `AGENT_SERVER_PORT` | `8000` |
| *(n/a)* | `OLLAMA_BASE_URL` | `http://localhost:11434` |

---

## Project structure

```
agent-starter/
├── agent_starter/          # Core library
│   ├── agent.py            # AgentKit class — main entry point
│   ├── graph.py            # LangGraph state graph
│   ├── state.py            # AgentState TypedDict
│   ├── config.py           # Config loader (YAML + env)
│   ├── llm.py              # Multi-provider LLM factory
│   ├── server.py           # FastAPI server
│   ├── memory/             # Short-term + long-term memory
│   └── tools/              # Tool registry + builtins
├── agents/                 # Agent definitions (YAML + persona markdown)
│   └── examples/           # Pre-built example agents
├── examples/               # Progressive code examples
│   ├── 01_basic/
│   ├── 02_intermediate/
│   └── 03_advanced/
└── tests/                  # Pytest test suite
```

---

## Contributing

PRs welcome. Keep it simple — the goal is a framework people can understand in 30 minutes, not a kitchen sink.

1. Fork the repo
2. Create a branch: `git checkout -b my-feature`
3. Run tests: `make test`
4. Open a PR

---

## License

MIT — see [LICENSE](LICENSE).
