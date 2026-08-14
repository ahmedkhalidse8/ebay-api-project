import hashlib
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

EBAY_VERIFICATION_TOKEN = os.getenv(
    "EBAY_VERIFICATION_TOKEN",
    "ebay-api-project-verification-2026"
)

EBAY_ENDPOINT = (
    "https://ebay-api-project.vercel.app/ebay/marketplace-deletion"
)


@app.get("/")
def home():
    return {"status": "eBay API project is running"}


@app.api_route(
    "/ebay/marketplace-deletion",
    methods=["GET", "POST"]
)
async def marketplace_deletion(request: Request):
    challenge_code = request.query_params.get("challenge_code")

    if challenge_code:
        challenge_response = hashlib.sha256(
            (
                challenge_code
                + EBAY_VERIFICATION_TOKEN
                + EBAY_ENDPOINT
            ).encode("utf-8")
        ).hexdigest()

        return JSONResponse(
            content={"challengeResponse": challenge_response}
        )

    if request.method == "POST":
        body = await request.json()

        print("Received eBay notification:")
        print(body)

        return {"status": "notification received"}

    return {"status": "endpoint is working"}