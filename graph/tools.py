from weight_Calculator.app import analyse
from image.image_processor import analyze_image
from video.video_processor import analyze_video
from langchain_core.tools import tool
from evidence import upload_evidence
import requests



@tool
def analyse_topic(topic:str) -> str:
    """Search social media for a topic."""
    return analyse(topic)

@tool
def image_tool(image_path: str) -> str:
    """
    Analyze an image from a clodinary url path and convert
    the visual content into a concise text description.

    Use this whenever the user provides an image path
    or asks to analyze an image.
    """
    return analyze_image(image_path)



@tool
def get_device_location():

    """
    this tool is used to fetch the user locartion
    """
    response = requests.get(
        "https://ipinfo.io/json",
        timeout=10
    )

    data = response.json()

    location = data.get("loc")

    if not location:
        return None

    latitude, longitude = location.split(",")

    return {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "city": data.get("city"),
        "region": data.get("region"),
        "country": data.get("country")
    }

@tool
def evidence_tool(file_path: str) -> str:
    """
    Upload an image or video from local storage to Cloudinary
    and return the evidence URL.
    """

    return upload_evidence(file_path)

@tool
def start_issue_reporting() -> str:
    """
    Start the citizen issue reporting workflow.

    Use this tool when the user clearly wants to report,
    submit, register, or complain about an issue.
    """
    return "ISSUE_REPORT_STARTED"

import os
import requests

from langchain_core.tools import tool


import os
import requests
from langchain_core.tools import tool



@tool
def submit_issue(
    issue_category: str,
    issue_weight: float,
    estimated_cost_range: str,
    issue_description: str,
    reporter_name: str,
    reporter_phone: str,
    issue_location: str,
    evidence: str | None
) -> str:

    """
    Submit the final confirmed citizen issue report to the Parakram API.

    Evidence must be a Cloudinary URL.
    Do not treat evidence as a local file path.
    """
    print("\n🔥🔥🔥 SUBMIT_ISSUE TOOL CALLED 🔥🔥🔥")
    print("EVIDENCE RECEIVED =", evidence)

    api_url = os.getenv("ISSUE_API_URL")

    if not api_url:
        return "ERROR: ISSUE_API_URL is not configured."

    endpoint = f"{api_url}/api/issues/report"

    payload = {
        "issue_category": issue_category,
        "issue_weight": issue_weight,
        "estimated_cost_range": estimated_cost_range,
        "issue_description": issue_description,
        "reported_by": {
            "name": reporter_name,
            "phone": reporter_phone
        },
        "issue_location": issue_location,
        "evidence": evidence
    }

    try:

        print("🔥 Calling:", endpoint)

        response = requests.post(
            endpoint,
            json=payload,
            timeout=30
        )

        print("🔥 API STATUS:", response.status_code)
        print("🔥 API RESPONSE:", response.text)

        response.raise_for_status()

        data = response.json()

        if data.get("success"):
            return (
                f"Issue reported successfully. "
                f"Report ID: #{data.get('report_id')}"
            )

        return "Issue submission failed."

    except requests.exceptions.RequestException as e:

        print("🔥 SUBMIT ERROR:", repr(e))

        return f"Failed to submit issue: {str(e)}"


TOOLS = [analyse_topic , image_tool,analyze_video , get_device_location , evidence_tool ,start_issue_reporting , submit_issue]