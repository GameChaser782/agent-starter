from __future__ import annotations

import base64
import os
from pathlib import Path

from langchain_core.tools import tool

_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def _load_image(path_or_url: str) -> tuple[str | None, str]:
    """Return (media_type, data). media_type=None means data is a URL."""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return None, path_or_url
    p = Path(path_or_url)
    media_type = _MEDIA_TYPES.get(p.suffix.lower(), "image/jpeg")
    data = base64.standard_b64encode(p.read_bytes()).decode()
    return media_type, data


@tool
def image_vision(
    image_path_or_url: str,
    prompt: str = "Describe this image in detail.",
) -> str:
    """Analyze an image using a vision model and return a description.

    Args:
        image_path_or_url: Local file path or public HTTPS URL of the image.
        prompt: What to ask about the image (default: describe it in detail).

    Requires ANTHROPIC_API_KEY (uses claude-haiku) or OPENAI_API_KEY (uses gpt-4o-mini).
    Anthropic is tried first if both keys are present.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return _vision_anthropic(image_path_or_url, prompt)
    if os.getenv("OPENAI_API_KEY"):
        return _vision_openai(image_path_or_url, prompt)
    return "Error: set ANTHROPIC_API_KEY or OPENAI_API_KEY to use image_vision."


def _vision_anthropic(path_or_url: str, prompt: str) -> str:
    try:
        import anthropic
    except ImportError:
        return "Error: run pip install 'agent-starter[anthropic]'"

    client = anthropic.Anthropic()
    media_type, data = _load_image(path_or_url)

    if media_type is None:
        image_block: dict = {"type": "image", "source": {"type": "url", "url": data}}
    else:
        image_block = {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data},
        }

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [image_block, {"type": "text", "text": prompt}],
                }
            ],
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error: {e}"


def _vision_openai(path_or_url: str, prompt: str) -> str:
    try:
        import openai
    except ImportError:
        return "Error: run pip install 'agent-starter[openai]'"

    client = openai.OpenAI()
    media_type, data = _load_image(path_or_url)
    url = data if media_type is None else f"data:{media_type};base64,{data}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": url}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
