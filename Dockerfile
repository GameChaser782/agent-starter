FROM python:3.12-slim

WORKDIR /app

# Install deps first for layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[anthropic,openai,search]"

# Copy source
COPY agent_starter/ ./agent_starter/
COPY agents/ ./agents/

EXPOSE 8000

ENV AGENT_PROVIDER=ollama
ENV AGENT_MODEL=llama3.2
ENV AGENT_SERVER_HOST=0.0.0.0
ENV AGENT_SERVER_PORT=8000

CMD ["agent-starter", "serve"]
