import os

import cloudinary
import cloudinary.uploader

from dotenv import load_dotenv
from langchain_core.tools import tool


load_dotenv()


# --------------------------------------------------
# Cloudinary configuration
# --------------------------------------------------

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


# --------------------------------------------------
# Upload evidence
# --------------------------------------------------

def upload_evidence(file_path: str) -> str:

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    result = cloudinary.uploader.upload(
        file_path,
        folder="parakram/evidence"
    )

    return result["secure_url"]


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    file_path = r"C:\Users\soura\OneDrive\Desktop\Parakram\code\image\test.jpeg"

    url = upload_evidence(file_path)

    print("\nCLOUDINARY UPLOAD SUCCESS")
    print("=" * 50)
    print(url)