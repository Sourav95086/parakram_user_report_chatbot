from datetime import datetime, timezone


def clamp(value, minimum=0, maximum=100):

    return max(
        minimum,
        min(value, maximum)
    )


def normalize(value, minimum, maximum):

    if maximum == minimum:
        return 0

    score = (
        (value - minimum)
        /
        (maximum - minimum)
    ) * 100

    return clamp(score)


def calculate_volume_score(posts):

    if not posts:
        return 0

    post_count = len(posts)

    # For V0:
    # 100 posts = 100 score

    score = min(
        (post_count / 100) * 100,
        100
    )

    return round(score, 2)


def calculate_engagement_score(posts):

    if not posts:
        return 0

    engagement_rates = []

    for post in posts:

        views = max(
            post.get("views", 1),
            1
        )

        engagement = (
            post.get("likes", 0)
            +
            post.get("comments", 0)
            +
            post.get("shares", 0)
        )

        rate = engagement / views

        engagement_rates.append(rate)

    average_rate = (
        sum(engagement_rates)
        /
        len(engagement_rates)
    )

    # Approximate normalization.
    # 10% average engagement = 100.

    score = (
        average_rate / 0.10
    ) * 100

    return round(
        clamp(score),
        2
    )


def calculate_discussion_score(posts):

    if not posts:
        return 0

    scores = []

    for post in posts:

        comments = post.get(
            "comments",
            0
        )

        replies = post.get(
            "replies",
            0
        )

        views = max(
            post.get("views", 1),
            1
        )

        comment_ratio = (
            comments / views
        )

        reply_ratio = (
            replies / max(comments, 1)
        )

        score = (

            min(
                comment_ratio / 0.02,
                1
            ) * 60

            +

            min(
                reply_ratio,
                1
            ) * 40

        )

        scores.append(score)

    return round(
        clamp(
            sum(scores) / len(scores)
        ),
        2
    )


def calculate_recency_score(posts):

    if not posts:
        return 0

    now = datetime.now(
        timezone.utc
    )

    scores = []

    for post in posts:

        created_at = post.get(
            "created_at"
        )

        try:

            created = datetime.fromisoformat(
                created_at
            )

            if created.tzinfo is None:

                created = created.replace(
                    tzinfo=timezone.utc
                )

            age_hours = (
                now - created
            ).total_seconds() / 3600

        except Exception:

            age_hours = 168

        # 0 hours = 100
        # 168 hours = 0

        score = max(
            0,
            100 - (
                age_hours / 168
            ) * 100
        )

        scores.append(score)

    return round(
        sum(scores) / len(scores),
        2
    )


def calculate_diversity_score(posts):

    if not posts:
        return 0

    authors = set()

    for post in posts:

        author = post.get(
            "author_id"
        )

        if author:
            authors.add(author)

    unique_authors = len(authors)

    total_posts = len(posts)

    ratio = (
        unique_authors
        /
        max(total_posts, 1)
    )

    return round(
        clamp(ratio * 100),
        2
    )


def calculate_platform_scores(posts):

    return {

        "volume": calculate_volume_score(
            posts
        ),

        "engagement": calculate_engagement_score(
            posts
        ),

        "discussion": calculate_discussion_score(
            posts
        ),

        "recency": calculate_recency_score(
            posts
        ),

        "diversity": calculate_diversity_score(
            posts
        )
    }


def calculate_topic_weight(
    volume_score,
    engagement_score,
    discussion_score,
    recency_score,
    diversity_score
):

    weight = (

        volume_score * 0.20

        +

        engagement_score * 0.25

        +

        discussion_score * 0.25

        +

        recency_score * 0.15

        +

        diversity_score * 0.15

    )

    return round(
        clamp(weight),
        2
    )