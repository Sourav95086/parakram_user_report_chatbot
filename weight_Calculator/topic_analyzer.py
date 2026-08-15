def analyze_topic(state):

    topic = state["topic"]

    queries = [

        topic,

        f"{topic} debate",

        f"{topic} discussion",

        f"{topic} opinion",

        f"{topic} controversy"

    ]

    return {

        "search_queries": queries

    }