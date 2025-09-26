import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
endpoint = os.getenv("AZURE_CV_ENDPOINT")
key = os.getenv("AZURE_CV_KEY")

if not endpoint or not key:
    raise RuntimeError("Missing AZURE_CV_ENDPOINT or AZURE_CV_KEY")

def read_image(uri: str) -> str:
    """
    Call Azure Computer Vision OCR (Read API v3.2).
    Supports both remote URLs and local file paths.
    """
    ocr_url = endpoint + "/vision/v3.2/read/analyze"
    headers = {"Ocp-Apim-Subscription-Key": key}

    # If uri is a local file path, upload the image
    if os.path.exists(uri):
        print("Uploading local file:", uri)
        with open(uri, "rb") as f:
            data = f.read()
        response = requests.post(
            ocr_url,
            headers={**headers, "Content-Type": "application/octet-stream"},
            data=data
        )
    else:
        # Otherwise, treat as remote URL
        print("Fetching remote URL:", uri)
        response = requests.post(
            ocr_url,
            headers={**headers, "Content-Type": "application/json"},
            json={"url": uri}
        )

    if response.status_code != 202:
        return f"Error: {response.status_code}, {response.text}"

    # Extract operation ID
    operation_url = response.headers["Operation-Location"]

    # Poll for result
    analysis = {}
    for _ in range(10):  # retry up to 10 times
        result = requests.get(operation_url, headers=headers)
        analysis = result.json()

        if "status" in analysis and analysis["status"] not in ["notStarted", "running"]:
            break

        time.sleep(1)

    # Parse results
    if analysis.get("status") == "succeeded":
        lines = []
        for readResult in analysis["analyzeResult"]["readResults"]:
            for line in readResult["lines"]:
                lines.append(line["text"])
        return " ".join(lines)

    return "error"
