from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

if TYPE_CHECKING:
    from .agent import AgentKit


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"
    user_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    thread_id: str


def create_app(agent: "AgentKit") -> FastAPI:
    app = FastAPI(
        title="agent-starter",
        description="LangGraph agent API — clone, customize, deploy.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"status": "ok", "agent": agent.config.name, "version": "0.1.0"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    def chat(req: ChatRequest):
        try:
            response = agent.chat(req.message, thread_id=req.thread_id, user_id=req.user_id)
            return ChatResponse(response=response, thread_id=req.thread_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/stream")
    async def stream(req: ChatRequest):
        async def token_generator() -> AsyncIterator[str]:
            async for token in agent.stream(req.message, thread_id=req.thread_id, user_id=req.user_id):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(token_generator(), media_type="text/event-stream")

    @app.get("/memory/{user_id}")
    def get_memory(user_id: str):
        """View stored long-term memories for a user."""
        from .memory.long_term import SQLiteLongTermMemory
        import os
        if not agent.config.long_term_memory:
            return {"memories": [], "note": "Long-term memory is disabled"}
        db_path = os.path.join(agent.config.memory_dir, "memory.db")
        mem = SQLiteLongTermMemory(db_path=db_path)
        memories = mem._backend.fetch_all(user_id)
        return {"user_id": user_id, "memories": memories}

    return app


def run_server(agent: "AgentKit", host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn
    app = create_app(agent)
    print(f"\n  agent-starter server running on http://{host}:{port}")
    print(f"  Agent: {agent.config.name}  |  Provider: {agent.config.model_provider}/{agent.config.model_name}")
    print(f"  Docs: http://{host}:{port}/docs\n")
    uvicorn.run(app, host=host, port=port)
