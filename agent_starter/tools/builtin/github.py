from __future__ import annotations

import base64
import os

import httpx

from langchain_core.tools import tool

_GH_API = "https://api.github.com"


def _headers() -> dict:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


@tool
def github_read_file(repo: str, path: str, ref: str = "main") -> str:
    """Read a file from a public GitHub repository.

    Args:
        repo: Owner/repo — e.g. "langchain-ai/langgraph"
        path: File path inside the repo — e.g. "README.md"
        ref: Branch, tag, or commit SHA (default "main")

    Set GITHUB_TOKEN for private repos and higher rate limits.
    """
    try:
        url = f"{_GH_API}/repos/{repo}/contents/{path}"
        r = httpx.get(url, headers=_headers(), params={"ref": ref}, timeout=15)
        if r.status_code == 404:
            return f"Error: {path} not found in {repo}@{ref}"
        r.raise_for_status()
        data = r.json()
        if data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode(errors="replace")
        return data.get("content", "(no content)")
    except Exception as e:
        return f"Error: {e}"


@tool
def github_list_issues(repo: str, state: str = "open", limit: int = 10) -> str:
    """List issues for a GitHub repository.

    Args:
        repo: Owner/repo — e.g. "langchain-ai/langgraph"
        state: "open", "closed", or "all" (default "open")
        limit: Max number of issues to return (default 10, max 100)

    Set GITHUB_TOKEN for private repos and higher rate limits.
    """
    try:
        url = f"{_GH_API}/repos/{repo}/issues"
        r = httpx.get(
            url,
            headers=_headers(),
            params={"state": state, "per_page": min(limit, 100)},
            timeout=15,
        )
        r.raise_for_status()
        issues = r.json()
        if not issues:
            return f"No {state} issues found in {repo}."
        lines = []
        for issue in issues[:limit]:
            tag = "PR" if "pull_request" in issue else "Issue"
            lines.append(f"#{issue['number']} [{tag}] {issue['title']}\n  {issue['html_url']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@tool
def github_get_issue(repo: str, issue_number: int) -> str:
    """Get the full details of a GitHub issue or pull request.

    Args:
        repo: Owner/repo — e.g. "langchain-ai/langgraph"
        issue_number: The issue or PR number

    Set GITHUB_TOKEN for private repos and higher rate limits.
    """
    try:
        url = f"{_GH_API}/repos/{repo}/issues/{issue_number}"
        r = httpx.get(url, headers=_headers(), timeout=15)
        if r.status_code == 404:
            return f"Error: #{issue_number} not found in {repo}"
        r.raise_for_status()
        i = r.json()
        body = (i.get("body") or "").strip()
        labels = ", ".join(lbl["name"] for lbl in i.get("labels", [])) or "none"
        return (
            f"#{i['number']} {i['title']}\n"
            f"State: {i['state']}  |  Author: {i['user']['login']}  |  Labels: {labels}\n"
            f"URL: {i['html_url']}\n\n"
            f"{body or '(no description)'}"
        )
    except Exception as e:
        return f"Error: {e}"
