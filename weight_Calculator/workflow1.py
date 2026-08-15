from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .state import TopicState

from .topic_analyzer import (
    analyze_topic
)

from .explainer import (
    generate_explanation
)

from .x_source import XSource

from .instagram_source import (
    InstagramSource
)

from .topic_weight import (
    calculate_platform_scores,
    calculate_topic_weight
)


def collect_social_data(state):

    topic = state["topic"]

    x_source = XSource()

    instagram_source = (
        InstagramSource()
    )

    x_posts = (
        x_source.search_topic(topic)
    )

    instagram_posts = (
        instagram_source.search_topic(
            topic
        )
    )

    return {

        "x_posts": x_posts,

        "instagram_posts":
            instagram_posts

    }


def calculate_scores(state):

    x_posts = state[
        "x_posts"
    ]

    instagram_posts = state[
        "instagram_posts"
    ]

    x_scores = calculate_platform_scores(
        x_posts
    )

    instagram_scores = (
        calculate_platform_scores(
            instagram_posts
        )
    )

    # Combine platforms.
    # Currently equal weighting.

    volume = (
        x_scores["volume"]
        +
        instagram_scores["volume"]
    ) / 2

    engagement = (
        x_scores["engagement"]
        +
        instagram_scores["engagement"]
    ) / 2

    discussion = (
        x_scores["discussion"]
        +
        instagram_scores["discussion"]
    ) / 2

    recency = (
        x_scores["recency"]
        +
        instagram_scores["recency"]
    ) / 2

    diversity = (
        x_scores["diversity"]
        +
        instagram_scores["diversity"]
    ) / 2

    return {

        "x_volume_score":
            x_scores["volume"],

        "x_engagement_score":
            x_scores["engagement"],

        "x_discussion_score":
            x_scores["discussion"],

        "x_recency_score":
            x_scores["recency"],

        "x_diversity_score":
            x_scores["diversity"],

        "instagram_volume_score":
            instagram_scores["volume"],

        "instagram_engagement_score":
            instagram_scores["engagement"],

        "instagram_discussion_score":
            instagram_scores["discussion"],

        "instagram_recency_score":
            instagram_scores["recency"],

        "instagram_diversity_score":
            instagram_scores["diversity"],

        "volume_score":
            round(volume, 2),

        "engagement_score":
            round(engagement, 2),

        "discussion_score":
            round(discussion, 2),

        "recency_score":
            round(recency, 2),

        "diversity_score":
            round(diversity, 2)

    }


def calculate_weight(state):

    weight = calculate_topic_weight(

        state["volume_score"],

        state["engagement_score"],

        state["discussion_score"],

        state["recency_score"],

        state["diversity_score"]

    )

    return {

        "topic_weight": weight

    }


def build_graph():

    workflow = StateGraph(
        TopicState
    )

    workflow.add_node(
        "analyze_topic",
        analyze_topic
    )

    workflow.add_node(
        "collect_social_data",
        collect_social_data
    )

    workflow.add_node(
        "calculate_scores",
        calculate_scores
    )

    workflow.add_node(
        "calculate_weight",
        calculate_weight
    )

    workflow.add_node(
        "generate_explanation",
        generate_explanation
    )

    workflow.add_edge(
        START,
        "analyze_topic"
    )

    workflow.add_edge(
        "analyze_topic",
        "collect_social_data"
    )

    workflow.add_edge(
        "collect_social_data",
        "calculate_scores"
    )

    workflow.add_edge(
        "calculate_scores",
        "calculate_weight"
    )

    workflow.add_edge(
        "calculate_weight",
        "generate_explanation"
    )

    workflow.add_edge(
        "generate_explanation",
        END
    )

    return workflow.compile()