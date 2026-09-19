import os
import base64

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import requests
from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------
# Configuration
# --------------------------------------------------

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0
)


# --------------------------------------------------
# Image → Text
# --------------------------------------------------



def analyze_image(image_url: str) -> str:

    # -----------------------------------------
    # Download image from Cloudinary
    # -----------------------------------------

    response = requests.get(
        image_url,
        timeout=30
    )

    if response.status_code != 200:
        raise ValueError(
            f"Could not download image. "
            f"HTTP status: {response.status_code}"
        )

    image_bytes = response.content

    # -----------------------------------------
    # Get MIME type
    # -----------------------------------------

    mime_type = response.headers.get(
        "Content-Type",
        ""
    ).split(";")[0].lower()

    supported_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if mime_type not in supported_types:
        raise ValueError(
            "Unsupported image format. "
            "Use JPG, JPEG, PNG or WEBP."
        )

    # -----------------------------------------
    # Convert image to base64
    # -----------------------------------------

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    # -----------------------------------------
    # Prompt + image
    # -----------------------------------------

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """
Analyze the image for use by another AI system.

Return ONLY a concise summary of the main situation
or issue visible in the image.

Include:
- What the image shows
- The main issue/problem
- Important visible details
- Relevant damage, obstruction, or hazard

Do NOT provide:
- Step-by-step reasoning
- Analysis process
- Section-by-section descriptions
- Bullet points
- Headings
- <think> tags
- Discussion of how you analyzed the image

Do not speculate or invent information.

Output only one short paragraph of approximately 1-3 sentences.
"""
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": (
                        f"data:{mime_type};"
                        f"base64,{image_base64}"
                    )
                }
            }
        ]
    )

    # -----------------------------------------
    # Vision model
    # -----------------------------------------

    response = llm.invoke([message])

    return response.content.strip()


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    image_path = "test.jpeg"
    result = analyze_image(image_path)

    print("\nIMAGE ANALYSIS")
    print("=" * 50)
    print(result)