from email.utils import parsedate_to_datetime

import feedparser

from viral_publisher.models import Story


def collect_stories(config: dict) -> list[Story]:
    feeds = config.get("feeds", [])
    max_sources = int(config.get("content", {}).get("max_sources", 8))
    stories: list[Story] = []

    for feed in feeds:
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries[:3]:
            stories.append(
                Story(
                    title=entry.get("title", "Untitled"),
                    url=entry.get("link", ""),
                    source=feed.get("name", "Unknown source"),
                    summary=_clean_summary(entry.get("summary", "")),
                    published=_normalize_date(entry.get("published", "")),
                )
            )

    return stories[:max_sources]


def _clean_summary(value: str) -> str:
    return " ".join(value.replace("\n", " ").split())[:320]


def _normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value
