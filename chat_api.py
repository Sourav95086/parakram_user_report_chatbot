from dotenv import load_dotenv

load_dotenv()
from image.image_processor import analyze_image

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from graph.agent import chatbot
from langchain_core.messages import HumanMessage


app = FastAPI(
    title="Parakram Issue Reporter",
    description="LangGraph-based citizen issue reporting API",
    version="1.0.0"
)


# ==========================================
# REQUEST SCHEMA
# ==========================================

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    image_url: str | None = None
    video_url: str | None = None


# ==========================================
# RESPONSE SCHEMA
# ==========================================

class ChatResponse(BaseModel):
    success: bool
    response: str
    thread_id: str


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def root():

    return {
        "success": True,
        "message": "Parakram Issue Reporter API is running 🚀"
    }

import os

import cloudinary
import cloudinary.uploader

from fastapi import FastAPI, HTTPException, UploadFile, File


# ------------------------------------------
# Cloudinary configuration
# ------------------------------------------

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


# ------------------------------------------
# Upload image
# ------------------------------------------

@app.post("/upload-image")
async def upload_image(
    image: UploadFile = File(...)
):

    try:

        # Read uploaded file
        file_data = await image.read()

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_data,
            folder="parakram/evidence",
            resource_type="image"
        )

        return {
            "success": True,
            "message": "Image uploaded successfully",
            "url": result["secure_url"],
            "public_id": result["public_id"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )

@app.post("/upload-video")
async def upload_video(
    video: UploadFile = File(...)
):
    try:

        # Read uploaded video
        video_data = await video.read()

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            video_data,
            folder="parakram/evidence",
            resource_type="video"
        )

        return {
            "success": True,
            "message": "Video uploaded successfully",
            "url": result["secure_url"],
            "public_id": result["public_id"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Video upload failed: {str(e)}"
        )


# ==========================================
# CHAT ENDPOINT
# ==========================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        # =====================================================
        # THREAD ID
        # =====================================================

        thread_id = request.thread_id

        if not thread_id:
            thread_id = "default-thread"

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # =====================================================
        # USER MESSAGE
        # =====================================================

        message = request.message or ""

        # =====================================================
        # ATTACH IMAGE URL
        # =====================================================

        if request.image_url:

            message += (
                "\n\n[IMAGE_URL]\n"
                f"{request.image_url}\n"
                "[/IMAGE_URL]"
            )

        # =====================================================
        # ATTACH VIDEO URL
        # =====================================================

        if request.video_url:

            message += (
                "\n\n[VIDEO_URL]\n"
                f"{request.video_url}\n"
                "[/VIDEO_URL]"
            )

        # =====================================================
        # DEBUG
        # =====================================================

        print("\n==============================")
        print("CHAT REQUEST")
        print("==============================")
        print("Thread ID:", thread_id)
        print("Message:", request.message)
        print("Image URL:", request.image_url)
        print("Video URL:", request.video_url)

        # =====================================================
        # INVOKE LANGGRAPH
        # =====================================================

        result = chatbot.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=message
                    )
                ]
            },
            config=config
        )

        # =====================================================
        # CHECK RESULT
        # =====================================================

        if not result:

            raise Exception(
                "Chatbot returned an empty result"
            )

        if "messages" not in result:

            raise Exception(
                "Chatbot result does not contain 'messages'"
            )

        messages = result["messages"]

        if not messages:

            raise Exception(
                "Chatbot returned an empty messages list"
            )

        last_message = messages[-1]

        response_content = last_message.content

        # =====================================================
        # HANDLE NON-STRING CONTENT
        # =====================================================

        if isinstance(response_content, list):

            text_parts = []

            for item in response_content:

                if isinstance(item, dict):

                    if item.get("type") == "text":

                        text_parts.append(
                            item.get("text", "")
                        )

                elif isinstance(item, str):

                    text_parts.append(item)

            response_content = "\n".join(
                text_parts
            )

        # =====================================================
        # RETURN RESPONSE
        # =====================================================

        print("\n==============================")
        print("CHAT RESPONSE")
        print("==============================")
        print(response_content)

        return ChatResponse(
            success=True,
            response=str(response_content),
            thread_id=thread_id
        )

    except Exception as e:

        # =====================================================
        # PRINT ACTUAL ERROR
        # =====================================================

        print("\n==============================")
        print("CHAT ERROR")
        print("==============================")
        print(type(e).__name__)
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/test-image")
def test_image(image_url: str):

    try:

        result = analyze_image(image_url)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )