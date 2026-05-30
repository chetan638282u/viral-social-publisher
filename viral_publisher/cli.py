import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from viral_publisher.config import load_config
from viral_publisher.content import create_draft
from viral_publisher.media import create_original_audio, create_short_video, create_text_image
from viral_publisher.models import DraftPost
from viral_publisher.publishers import get_publisher
from viral_publisher.sources import collect_stories


OUTPUT_DIR = Path("output")
DRAFT_PATH = OUTPUT_DIR / "draft.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and approve daily social content drafts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser("draft", help="Collect sources and create a draft.")
    draft_parser.add_argument("--config", default="config.example.yaml")
    draft_parser.add_argument("--videos", type=int, choices=[1, 2], default=None)

    approve_parser = subparsers.add_parser("approve", help="Publish the latest approved draft.")
    approve_parser.add_argument("--platforms", nargs="+", default=["dry_run"])

    daily_parser = subparsers.add_parser("daily", help="Create a draft and ask for human confirmation.")
    daily_parser.add_argument("--config", default="config.example.yaml")
    daily_parser.add_argument("--videos", type=int, choices=[1, 2], default=None)

    telegram_parser = subparsers.add_parser("telegram-request", help="Send today's draft to Telegram for approval.")
    telegram_parser.add_argument("--config", default="config.example.yaml")
    telegram_parser.add_argument("--videos", type=int, choices=[1, 2], default=None)

    subparsers.add_parser("telegram-bot", help="Run the Telegram approval listener.")

    args = parser.parse_args()
    load_dotenv()

    if args.command == "draft":
        draft = build_draft(args.config, video_count=args.videos)
        print_draft_summary(draft)
        return

    if args.command == "approve":
        draft = load_draft()
        results = [get_publisher(platform).publish(draft) for platform in args.platforms]
        print(json.dumps(results, indent=2))
        return

    if args.command == "daily":
        draft = build_draft(args.config, video_count=args.videos)
        print_draft_summary(draft)
        answer = input("\nPost this now? Type YES to publish dry run, or anything else to cancel: ")
        if answer.strip() == "YES":
            result = get_publisher("dry_run").publish(draft)
            print(json.dumps(result, indent=2))
        else:
            print("Cancelled. Draft saved for later approval.")
        return

    if args.command == "telegram-request":
        from viral_publisher.telegram_approval import send_approval_request

        result = send_approval_request(args.config, video_count=args.videos)
        print(json.dumps(result, indent=2))
        return

    if args.command == "telegram-bot":
        from viral_publisher.telegram_approval import run_approval_bot

        run_approval_bot()


def build_draft(config_path: str, video_count: int | None = None) -> DraftPost:
    config = load_config(config_path)
    stories = collect_stories(config)
    audio_path = create_original_audio(OUTPUT_DIR)
    count = video_count or int(config.get("content", {}).get("daily_video_count", 1))
    count = max(1, min(count, 2))
    draft = create_draft(stories, "", audio_path=audio_path, config=config)
    image_path = create_text_image(draft.hook or draft.topic or "Daily Tech Signal", OUTPUT_DIR)
    draft.image_path = image_path
    video_paths = []
    for index in range(1, count + 1):
        video_paths.append(create_short_video(image_path, audio_path, OUTPUT_DIR, filename=f"short_video_{index}.mp4"))
    draft.video_paths = video_paths
    draft.video_path = video_paths[0]
    save_draft(draft)
    return draft


def save_draft(draft: DraftPost) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_PATH.write_text(json.dumps(draft.to_dict(), indent=2), encoding="utf-8")
    (OUTPUT_DIR / "short_script.txt").write_text(draft.short_script, encoding="utf-8")
    (OUTPUT_DIR / "video_manifest.json").write_text(json.dumps(draft.video_paths, indent=2), encoding="utf-8")


def load_draft() -> DraftPost:
    if not DRAFT_PATH.exists():
        raise FileNotFoundError("No draft found. Run: python -m viral_publisher draft")
    return DraftPost.from_dict(json.loads(DRAFT_PATH.read_text(encoding="utf-8")))


def print_draft_summary(draft: DraftPost) -> None:
    print("\nDraft created")
    print("=" * 40)
    print(f"Hook: {draft.hook}")
    print(f"Image: {draft.image_path}")
    print(f"Video: {draft.video_path}")
    print(f"All videos: {', '.join(draft.video_paths)}")
    print(f"Audio: {draft.audio_path}")
    print("\nCaption:")
    print(draft.caption)
    print("\nShort video script:")
    print(draft.short_script)
    print("\nSources:")
    for story in draft.sources:
        print(f"- {story.title} | {story.source} | {story.url}")
