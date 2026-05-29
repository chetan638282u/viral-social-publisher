from collections import Counter
import json
import re

import requests

from viral_publisher.ai_writer import generate_original_post
from viral_publisher.models import DraftPost, Story


STOPWORDS = {
    "about",
    "after",
    "again",
    "from",
    "into",
    "more",
    "over",
    "that",
    "the",
    "this",
    "with",
    "your",
    "will",
}


def create_draft(
    stories: list[Story],
    image_path: str,
    video_path: str = "",
    audio_path: str = "",
    config: dict | None = None,
    video_paths: list[str] | None = None,
) -> DraftPost:
    if not stories:
        raise ValueError("No stories found. Add working RSS feeds to config.example.yaml.")

    try:
        ai_post = generate_original_post(config or {}, stories)
    except (requests.RequestException, KeyError, IndexError, ValueError, TypeError, json.JSONDecodeError):
        ai_post = None
    if ai_post:
        keywords = _extract_keywords(stories)
        fallback_topic = _make_topic(keywords)
        fallback_hook = _make_hook(keywords)
        fallback_hashtags = _make_hashtags(keywords)
        return DraftPost(
            topic=ai_post.get("topic") or fallback_topic,
            hook=ai_post.get("hook") or fallback_hook,
            caption=ai_post.get("caption") or _make_caption(stories, fallback_hashtags, fallback_topic),
            hashtags=list(ai_post.get("hashtags") or fallback_hashtags),
            short_script=ai_post.get("short_script") or _make_short_script(stories, fallback_topic),
            sources=stories[:4],
            image_path=image_path,
            video_path=video_path,
            video_paths=video_paths or ([video_path] if video_path else []),
            audio_path=audio_path,
        )

    keywords = _extract_keywords(stories)
    topic = _make_topic(keywords)
    hook = _make_hook(keywords)
    hashtags = _make_hashtags(keywords)
    caption = _make_caption(stories, hashtags, topic)
    short_script = _make_short_script(stories, topic)

    return DraftPost(
        topic=topic,
        hook=hook,
        caption=caption,
        hashtags=hashtags,
        short_script=short_script,
        sources=stories[:4],
        image_path=image_path,
        video_path=video_path,
        video_paths=video_paths or ([video_path] if video_path else []),
        audio_path=audio_path,
    )


def _extract_keywords(stories: list[Story]) -> list[str]:
    words: list[str] = []
    for story in stories:
        words.extend(re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", f"{story.title} {story.summary}"))

    counts = Counter(word.lower().strip("-") for word in words if word.lower() not in STOPWORDS)
    return [word for word, _ in counts.most_common(8)]


def _make_topic(keywords: list[str]) -> str:
    keyword = keywords[0].replace("-", " ").title() if keywords else "Technology"
    return f"{keyword} shift worth watching"


def _make_hook(keywords: list[str]) -> str:
    keyword = keywords[0].replace("-", " ").title() if keywords else "Tech"
    return f"A fast {keyword} shift is happening right now"


def _make_hashtags(keywords: list[str]) -> list[str]:
    base = ["AI", "TechNews", "Innovation", "DailyBrief"]
    generated = [word.replace("-", "").title() for word in keywords[:6]]
    unique = []
    for tag in base + generated:
        if tag and tag not in unique:
            unique.append(tag)
    return [f"#{tag}" for tag in unique[:10]]


def _make_caption(stories: list[Story], hashtags: list[str], topic: str) -> str:
    sources = ", ".join(story.source for story in stories[:3])
    return (
        f"{topic}\n\n"
        "Quick take: several trusted tech sources are pointing at a change that could affect how people build, play, work, or communicate online.\n\n"
        f"Sources checked: {sources}\n\n"
        "What do you think: useful breakthrough or just hype?\n\n"
        f"{' '.join(hashtags)}"
    )


def _make_short_script(stories: list[Story], topic: str) -> str:
    sources = ", ".join(story.source for story in stories[:3])
    return (
        "0-2s: Show headline card.\n"
        f"Voiceover: \"Stop scrolling. There is a new {topic.lower()}.\"\n\n"
        "3-10s: Show three fast bullet cards.\n"
        f"Voiceover: \"The signal comes from multiple sources, including {sources}.\"\n\n"
        "11-18s: Show why it matters.\n"
        "Voiceover: \"This matters because it could change how people use tech this week.\"\n\n"
        "19-25s: End with a question.\n"
        "Voiceover: \"Breakthrough or hype? Comment your take.\""
    )
