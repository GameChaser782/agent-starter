from __future__ import annotations

import os

from langchain_core.tools import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for up-to-date information. Returns a summary of top results.

    Requires either TAVILY_API_KEY (recommended) or falls back to DuckDuckGo (no key needed).
    """
    tavily_key = os.getenv("TAVILY_API_KEY")

    if tavily_key:
        return _tavily_search(query, max_results, tavily_key)
    return _ddg_search(query, max_results)


def _tavily_search(query: str, max_results: int, api_key: str) -> str:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=max_results)
        results = response.get("results", [])
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(f"**{r.get('title', 'No title')}**\n{r.get('url', '')}\n{r.get('content', '')}\n")
        return "\n---\n".join(lines)
    except ImportError:
        return "Tavily not installed. Run: pip install 'agent-starter[search]'"
    except Exception as e:
        return f"Search error: {e}"


def _ddg_search(query: str, max_results: int) -> str:
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        ddg = DuckDuckGoSearchRun()
        return ddg.run(query)
    except Exception as e:
        return f"DuckDuckGo search error: {e}. Set TAVILY_API_KEY for reliable search."
