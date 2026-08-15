
from typing import TypedDict, List, Dict


class TopicState(TypedDict, total=False):

    # Input
    topic: str

    # Internal data
    x_posts: List[Dict]
    instagram_posts: List[Dict]

    # Platform metrics
    x_volume_score: float
    x_engagement_score: float
    x_discussion_score: float
    x_recency_score: float
    x_diversity_score: float

    instagram_volume_score: float
    instagram_engagement_score: float
    instagram_discussion_score: float
    instagram_recency_score: float
    instagram_diversity_score: float

    # Final combined metrics
    volume_score: float
    engagement_score: float
    discussion_score: float
    recency_score: float
    diversity_score: float

    # Final weight
    topic_weight: float
