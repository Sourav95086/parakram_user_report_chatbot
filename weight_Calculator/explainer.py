from langchain_groq import ChatGroq

from .config import GROQ_API_KEY


def generate_explanation(state):

    topic = state["topic"]

    weight = state["topic_weight"]

    volume = state["volume_score"]

    engagement = state["engagement_score"]

    discussion = state["discussion_score"]

    recency = state["recency_score"]

    diversity = state["diversity_score"]

    if not GROQ_API_KEY:

        return {

            "explanation": (
                f"The topic '{topic}' has a "
                f"social discussion weight of "
                f"{weight}/100."
            )

        }

    llm = ChatGroq(

        model="llama-3.3-70b-versatile",

        temperature=0.2,

        api_key=GROQ_API_KEY

    )

    prompt = f"""

You are a social media trend analyst.

Analyze this topic:

{topic}

Social discussion metrics:

Volume: {volume}/100
Engagement: {engagement}/100
Discussion: {discussion}/100
Recency: {recency}/100
Diversity: {diversity}/100

Overall Topic Weight:

{weight}/100

Explain why this topic received this score.

Keep the explanation concise.

Mention:

1. Overall strength
2. Strongest metric
3. Weakest metric
4. What the score means
5. Whether the topic appears highly discussable

Do not invent external facts.
Only interpret the provided metrics.
"""

    response = llm.invoke(prompt)

    return {

        "explanation": response.content

    }