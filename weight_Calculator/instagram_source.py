import random
from datetime import datetime, timedelta

from .base import SocialSource


class InstagramSource(SocialSource):

    def search_topic(self, topic: str):

        posts = []

        for i in range(100):

            views = random.randint(
                1_000,
                3_000_000
            )

            likes = int(
                views * random.uniform(0.02, 0.15)
            )

            comments = int(
                likes * random.uniform(0.03, 0.4)
            )

            shares = int(
                likes * random.uniform(0.02, 0.25)
            )

            hours_ago = random.randint(
                1,
                168
            )

            created_at = (
                datetime.now()
                - timedelta(hours=hours_ago)
            ).isoformat()

            post = {

                "platform": "instagram",

                "text": f"Discussion about {topic}",

                "likes": likes,

                "comments": comments,

                "shares": shares,

                "views": views,

                "created_at": created_at,

                "author_id": (
                    f"instagram_user_"
                    f"{random.randint(1, 500)}"
                ),

                "replies": random.randint(
                    1,
                    max(comments, 1)
                )
            }

            posts.append(post)

        return posts