import os
import base64
import secrets
import requests

from datetime import date, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse


app = FastAPI()


# ============================================================
# eBay API URLs
# ============================================================

EBAY_AUTH_URL = (
    "https://auth.ebay.com/oauth2/authorize"
)

EBAY_TOKEN_URL = (
    "https://api.ebay.com/identity/v1/oauth2/token"
)

EBAY_TRAFFIC_URL = (
    "https://api.ebay.com/sell/analytics/v1/traffic_report"
)

EBAY_ORDERS_URL = (
    "https://api.ebay.com/sell/fulfillment/v1/order"
)

EBAY_INVENTORY_URL = (
    "https://api.ebay.com/sell/inventory/v1/inventory_item"
)


# ============================================================
# Environment helper
# ============================================================

def get_env(name: str) -> str:

    value = os.getenv(name)

    if not value:
        raise HTTPException(
            status_code=500,
            detail=f"Missing environment variable: {name}"
        )

    return value


# ============================================================
# Home
# ============================================================

@app.get("/")
def home():

    return {
        "status": "SalesAnalytics API is running"
    }


# ============================================================
# eBay Marketplace Deletion Endpoint
# ============================================================

@app.get("/ebay/marketplace-deletion")
def marketplace_deletion():

    return {
        "status": "endpoint is working"
    }


# ============================================================
# Debug environment
# ============================================================

@app.get("/debug/env")
def debug_env():

    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    ru_name = os.getenv("EBAY_RU_NAME")
    refresh_token = os.getenv("EBAY_REFRESH_TOKEN")

    return {
        "client_id_present": bool(client_id),
        "client_secret_present": bool(client_secret),
        "ru_name_present": bool(ru_name),
        "refresh_token_present": bool(refresh_token),
        "refresh_token_is_placeholder": (
            refresh_token == "your_actual_refresh_token"
        ),
    }


# ============================================================
# Step 1: eBay Login
# ============================================================

@app.get("/ebay/login")
def ebay_login():

    client_id = get_env("EBAY_CLIENT_ID")
    ru_name = get_env("EBAY_RU_NAME")

    state = secrets.token_urlsafe(32)

    scopes = [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly",
    ]

    scope_string = " ".join(scopes)

    authorization_url = (
        f"{EBAY_AUTH_URL}"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={ru_name}"
        f"&scope={scope_string}"
        f"&state={state}"
    )

    return RedirectResponse(
        url=authorization_url
    )


# ============================================================
# Step 2: OAuth Callback
# ============================================================

@app.get("/ebay/oauth/callback")
def ebay_oauth_callback(
    code: str,
    state: str | None = None
):

    client_id = get_env("EBAY_CLIENT_ID")
    client_secret = get_env("EBAY_CLIENT_SECRET")
    ru_name = get_env("EBAY_RU_NAME")

    credentials = (
        f"{client_id}:{client_secret}"
    )

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    token_headers = {
        "Content-Type": (
            "application/x-www-form-urlencoded"
        ),
        "Authorization": (
            f"Basic {encoded_credentials}"
        ),
    }

    token_request_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": ru_name,
    }

    token_response = requests.post(
        EBAY_TOKEN_URL,
        headers=token_headers,
        data=token_request_data,
        timeout=30,
    )

    if token_response.status_code != 200:

        raise HTTPException(
            status_code=token_response.status_code,
            detail={
                "message": (
                    "eBay OAuth token exchange failed"
                ),
                "ebay_response": (
                    token_response.text
                ),
            },
        )

    token_data = token_response.json()

    access_token = token_data.get(
        "access_token"
    )

    if not access_token:

        raise HTTPException(
            status_code=500,
            detail=(
                "eBay did not return an access token."
            ),
        )

    refresh_token = token_data.get(
        "refresh_token"
    )

    if not refresh_token:

        raise HTTPException(
            status_code=500,
            detail=(
                "eBay did not return a refresh token."
            ),
        )

    # ========================================================
    # TEMPORARY
    # Get the refresh token into Vercel environment variables
    # ========================================================

    return {
        "status": "OAuth successful",
        "refresh_token": refresh_token,
        "expires_in": token_data.get("expires_in"),
    }