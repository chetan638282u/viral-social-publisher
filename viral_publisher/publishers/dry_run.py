from pathlib import Path

from viral_publisher.models import DraftPost
from viral_publisher.publishers.base import Publisher


class DryRunPublisher(Publisher):
    def publish(self, draft: DraftPost) -> dict:
        output = Path("output") / "dry_run_post.txt"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            f"HOOK:\n{draft.hook}\n\nCAPTION:\n{draft.caption}\n\nSHORT SCRIPT:\n{draft.short_script}\n\n"
            f"IMAGE:\n{draft.image_path}\nVIDEO:\n{draft.video_path}\n"
            f"ALL VIDEOS:\n{chr(10).join(draft.video_paths)}\nAUDIO:\n{draft.audio_path}\n",
            encoding="utf-8",
        )
        return {"platform": "dry_run", "status": "saved", "path": str(output)}
