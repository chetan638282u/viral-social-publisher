import json
import os
from typing import Any

import requests

from viral_publisher.models import Story


def generate_original_post(config: dict, stories: list[Story]) -> dict[str, Any] | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    prompt = _build_prompt(config, stories)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    response.raise_for_status()
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_json(text)


def _build_prompt(config: dict, stories: list[Story]) -> str:
    brand = config.get("brand", {})
    source_notes = []
    for index, story in enumerate(stories[:6], start=1):
        source_notes.append(
            {
                "number": index,
                "title": story.title,
                "source": story.source,
                "summary_notes": story.summary[:220],
                "url": story.url,
            }
        )

    return (
        "You are writing original social media content from research notes.\n"
        "Do not copy sentences from the source notes. Do not invent facts. Do not make legal, medical, or financial advice.\n"
        "Write in this brand voice: "
        f"{brand.get('tone', 'clear, energetic, responsible')}.\n"
        f"Audience: {brand.get('audience', 'general tech audience')}.\n\n"
        "Return only valid JSON with these keys:\n"
        "topic, hook, caption, hashtags, short_script, image_title, video_titles\n"
        "Rules:\n"
        "- caption must be original and under 1200 characters.\n"
        "- hashtags must be an array of 6 to 10 tags with #.\n"
        "- short_script must be a 20-30 second vertical video script.\n"
        "- video_titles must be an array of 2 short titles.\n"
        "- include source names in caption, not long copied text.\n\n"
        f"Research notes:\n{json.dumps(source_notes, indent=2)}"
    )


def _parse_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    return json.loads(cleaned)
