import os

import requests

from viral_publisher.models import DraftPost
from viral_publisher.publishers.base import Publisher


class InstagramPublisher(Publisher):
    def publish(self, draft: DraftPost) -> dict:
        token = os.getenv("INSTAGRAM_ACCESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
        account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        public_image_url = os.getenv("PUBLIC_IMAGE_URL")
        public_video_url = os.getenv("PUBLIC_VIDEO_URL")
        version = os.getenv("META_GRAPH_VERSION")
        if not token or not account_id or not version:
            raise RuntimeError(
                "META_GRAPH_VERSION, INSTAGRAM_ACCESS_TOKEN, and INSTAGRAM_BUSINESS_ACCOUNT_ID are required."
            )
        if not public_image_url and not public_video_url:
            raise RuntimeError("PUBLIC_IMAGE_URL or PUBLIC_VIDEO_URL is required. Instagram's API needs a public media URL.")

        payload = {"caption": draft.caption, "access_token": token}
        if public_video_url:
            payload.update({"media_type": "REELS", "video_url": public_video_url})
        else:
            payload.update({"image_url": public_image_url})

        create = requests.post(
            f"https://graph.instagram.com/{version}/{account_id}/media",
            data=payload,
            timeout=30,
        )
        create.raise_for_status()
        creation_id = create.json()["id"]

        publish = requests.post(
            f"https://graph.instagram.com/{version}/{account_id}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=30,
        )
        publish.raise_for_status()
        return {"platform": "instagram", "status": "posted", "response": publish.json()}
