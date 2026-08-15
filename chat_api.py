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

        config = {
            "configurable": {
                "thread_id": request.thread_id
            }
        }

        message = request.message

        # -----------------------------------------
        # Attach image URL if provided
        # -----------------------------------------

        if request.image_url:

            message += (
                f"\n\n[IMAGE_URL]\n"
                f"{request.image_url}\n"
                f"[/IMAGE_URL]"
            )

        # -----------------------------------------
        # Attach video URL if provided
        # -----------------------------------------

        if request.video_url:

            message += (
                f"\n\n[VIDEO_URL]\n"
                f"{request.video_url}\n"
                f"[/VIDEO_URL]"
            )

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

        last_message = result["messages"][-1]

        return {
            "success": True,
            "response": last_message.content,
            "thread_id": request.thread_id
        }

    except Exception as e:

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