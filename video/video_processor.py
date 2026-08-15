import os
import cv2
import base64
import tempfile
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

load_dotenv()
# --------------------------------------------------
# Vision Model
# --------------------------------------------------

llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0
)


# --------------------------------------------------
# Extract representative frames
# --------------------------------------------------

def extract_frames(video_path: str, num_frames: int = 3):

    if not os.path.exists(video_path):
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(
            f"Could not open video: {video_path}"
        )

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:
        cap.release()
        raise ValueError("Video contains no frames.")

    actual_frames = min(num_frames, total_frames)

    if actual_frames == 1:
        frame_indices = [0]
    else:
        frame_indices = [
            int(i * (total_frames - 1) / (actual_frames - 1))
            for i in range(actual_frames)
        ]

    frames = []

    for index in frame_indices:

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            index
        )

        success, frame = cap.read()

        if success:
            frames.append(frame)

    cap.release()

    return frames


# --------------------------------------------------
# Resize + encode frame
# --------------------------------------------------

def frame_to_base64(frame, max_width=640):

    height, width = frame.shape[:2]

    if width > max_width:

        scale = max_width / width

        new_width = int(width * scale)
        new_height = int(height * scale)

        frame = cv2.resize(
            frame,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            65
        ]
    )

    if not success:
        raise ValueError("Could not encode video frame.")

    return base64.b64encode(
        encoded.tobytes()
    ).decode("utf-8")


# --------------------------------------------------
# VIDEO → TEXT
# --------------------------------------------------



@tool
def analyze_video(video_url: str) -> str:
    """
    Analyze a video from a URL and convert its visual
    content into a concise text description.

    The video is temporarily downloaded, frames are
    extracted, analyzed, and then the temporary file
    is removed.
    """

    temp_video_path = None

    try:

        # -----------------------------------------
        # Download video
        # -----------------------------------------

        response = requests.get(
            video_url,
            stream=True,
            timeout=60
        )

        if response.status_code != 200:
            raise ValueError(
                f"Could not download video. "
                f"HTTP status: {response.status_code}"
            )

        # -----------------------------------------
        # Create temporary file
        # -----------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False
        ) as temp_file:

            temp_video_path = temp_file.name

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:
                    temp_file.write(chunk)

        # -----------------------------------------
        # Extract frames
        # -----------------------------------------

        frames = extract_frames(
            temp_video_path,
            num_frames=2
        )

        if not frames:
            raise ValueError(
                "Could not extract frames from video."
            )

        # -----------------------------------------
        # Build vision request
        # -----------------------------------------

        content = [
            {
                "type": "text",
                "text": """
Analyze these frames taken from the same video.

Use the frames together to understand what is
happening throughout the video.

Return ONLY a concise summary for another AI system.

Include:
- What the video shows
- The main issue or situation
- Important visible details
- Damage, obstruction, or hazard if present

Focus on information that is actually visible
across the frames.

Do NOT:
- Describe each frame separately
- Provide step-by-step reasoning
- Provide bullet points
- Add headings
- Include <think> tags
- Speculate or invent information

Return only ONE short paragraph of approximately
1-3 sentences.
"""
            }
        ]

        # -----------------------------------------
        # Add extracted frames
        # -----------------------------------------

        for frame in frames:

            image_base64 = frame_to_base64(
                frame
            )

            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            "data:image/jpeg;base64,"
                            + image_base64
                        )
                    }
                }
            )

        # -----------------------------------------
        # Send to vision model
        # -----------------------------------------

        message = HumanMessage(
            content=content
        )

        result = llm.invoke(
            [message]
        )

        return result.content.strip()

    finally:

        # -----------------------------------------
        # Delete temporary video
        # -----------------------------------------

        if temp_video_path and os.path.exists(
            temp_video_path
        ):
            os.remove(temp_video_path)

# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    video_path = "test.mp4"

    result = analyze_video(
        video_path
    )

    print("\nVIDEO ANALYSIS")
    print("=" * 50)
    print(result)