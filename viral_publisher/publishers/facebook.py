import os

import requests

from viral_publisher.models import DraftPost
from viral_publisher.publishers.base import Publisher


class FacebookPublisher(Publisher):
    def publish(self, draft: DraftPost) -> dict:
        token = os.getenv("META_ACCESS_TOKEN")
        page_id = os.getenv("META_PAGE_ID")
        version = os.getenv("META_GRAPH_VERSION")
        if not token or not page_id or not version:
            raise RuntimeError("META_GRAPH_VERSION, META_ACCESS_TOKEN, and META_PAGE_ID are required for Facebook posting.")

        response = requests.post(
            f"https://graph.facebook.com/{version}/{page_id}/feed",
            data={"message": draft.caption, "access_token": token},
            timeout=30,
        )
        response.raise_for_status()
        return {"platform": "facebook", "status": "posted", "response": response.json()}
