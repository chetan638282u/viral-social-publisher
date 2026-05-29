from viral_publisher.models import DraftPost
from viral_publisher.publishers.base import Publisher


class YouTubePublisher(Publisher):
    def publish(self, draft: DraftPost) -> dict:
        raise RuntimeError(
            "YouTube Shorts upload needs OAuth and a real video file. "
            "Add google-api-python-client and OAuth flow before enabling this publisher."
        )
