import os

import requests

from viral_publisher.models import DraftPost
from viral_publisher.publishers.base import Publisher


class LinkedInPublisher(Publisher):
    def publish(self, draft: DraftPost) -> dict:
        token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        author = os.getenv("LINKEDIN_AUTHOR_URN")
        if not token or not author:
            raise RuntimeError("LINKEDIN_ACCESS_TOKEN and LINKEDIN_AUTHOR_URN are required for LinkedIn posting.")

        payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": draft.caption},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return {"platform": "linkedin", "status": "posted", "response": response.json() if response.text else {}}
