import random
from datetime import datetime, timedelta

from .base import SocialSource


class XSource(SocialSource):

    def search_topic(self, topic: str):

        posts = []

        for i in range(100):

            views = random.randint(
                500,
                2_000_000
            )

            likes = int(
                views * random.uniform(0.01, 0.12)
            )

            comments = int(
                likes * random.uniform(0.05, 0.5)
            )

            shares = int(
                likes * random.uniform(0.02, 0.3)
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

                "platform": "x",

                "text": f"Discussion about {topic}",

                "likes": likes,

                "comments": comments,

                "shares": shares,

                "views": views,

                "created_at": created_at,

                "author_id": f"x_user_{random.randint(1, 500)}",

                "replies": random.randint(
                    1,
                    max(comments, 1)
                )
            }

            posts.append(post)

        return posts