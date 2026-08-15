
from weight_Calculator.workflow1 import build_graph


def analyse(topic):

    topic = topic.strip()

    if not topic:
        return "Please enter a topic."

    try:

        graph = build_graph()

        result = graph.invoke({
            "topic": topic
        })

        # Return ONLY compact information
        # needed by the chatbot.

        return {
            "topic": result["topic"],
            "weight": result["topic_weight"],

            "metrics": {
                "volume": result["volume_score"],
                "engagement": result["engagement_score"],
                "discussion": result["discussion_score"],
                "recency": result["recency_score"],
                "diversity": result["diversity_score"]
            },

            "platforms": {
                "X": round(
                    (
                        result["x_volume_score"]
                        + result["x_engagement_score"]
                        + result["x_discussion_score"]
                        + result["x_recency_score"]
                        + result["x_diversity_score"]
                    ) / 5,
                    2
                ),

                "Instagram": round(
                    (
                        result["instagram_volume_score"]
                        + result["instagram_engagement_score"]
                        + result["instagram_discussion_score"]
                        + result["instagram_recency_score"]
                        + result["instagram_diversity_score"]
                    ) / 5,
                    2
                )
            }
        }

    except Exception as e:

        return {
            "error": str(e)
        }

