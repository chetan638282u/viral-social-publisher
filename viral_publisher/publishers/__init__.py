from viral_publisher.publishers.dry_run import DryRunPublisher
from viral_publisher.publishers.facebook import FacebookPublisher
from viral_publisher.publishers.instagram import InstagramPublisher
from viral_publisher.publishers.linkedin import LinkedInPublisher
from viral_publisher.publishers.youtube import YouTubePublisher


def get_publisher(name: str):
    publishers = {
        "dry_run": DryRunPublisher,
        "facebook": FacebookPublisher,
        "instagram": InstagramPublisher,
        "linkedin": LinkedInPublisher,
        "youtube": YouTubePublisher,
    }
    try:
        return publishers[name]()
    except KeyError as exc:
        raise ValueError(f"Unknown platform: {name}") from exc
