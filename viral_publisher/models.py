from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Story:
    title: str
    url: str
    source: str
    summary: str = ""
    published: str = ""


@dataclass
class DraftPost:
    topic: str
    hook: str
    caption: str
    hashtags: list[str]
    short_script: str
    sources: list[Story]
    image_path: str
    video_path: str = ""
    video_paths: list[str] = field(default_factory=list)
    audio_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "hook": self.hook,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "short_script": self.short_script,
            "sources": [story.__dict__ for story in self.sources],
            "image_path": self.image_path,
            "video_path": self.video_path,
            "video_paths": self.video_paths,
            "audio_path": self.audio_path,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DraftPost":
        return cls(
            topic=data["topic"],
            hook=data["hook"],
            caption=data["caption"],
            hashtags=list(data.get("hashtags", [])),
            short_script=data.get("short_script", ""),
            sources=[Story(**item) for item in data.get("sources", [])],
            image_path=data.get("image_path", ""),
            video_path=data.get("video_path", ""),
            video_paths=list(data.get("video_paths", [])),
            audio_path=data.get("audio_path", ""),
            created_at=data.get("created_at", ""),
        )
