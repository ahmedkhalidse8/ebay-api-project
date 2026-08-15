import os
import base64
import secrets
import requests

from pathlib import Path
from datetime import date, timedelta

from dotenv import load_dotenv, set_key

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR / ".env"

# Load environment variables from the project's .env file
load_dotenv(ENV_FILE, override=True)


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
# Helper: required environment variable
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
# Debug: Check environment configuration
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
        "env_file": str(ENV_FILE),
    }


# ============================================================
# Step 1: eBay Login
# ============================================================

@app.get("/ebay/login")
def ebay_login():

    client_id = get_env("EBAY_CLIENT_ID")
    ru_name = get_env("EBAY_RU_NAME")

    # --------------------------------------------------------
    # CSRF protection state
    # --------------------------------------------------------

    state = secrets.token_urlsafe(32)

    # --------------------------------------------------------
    # OAuth scopes
    # --------------------------------------------------------

    scopes = [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly",
    ]

    scope_string = " ".join(scopes)

    # --------------------------------------------------------
    # Build eBay authorization URL
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Load credentials
    # --------------------------------------------------------

    client_id = get_env("EBAY_CLIENT_ID")
    client_secret = get_env("EBAY_CLIENT_SECRET")
    ru_name = get_env("EBAY_RU_NAME")

    # --------------------------------------------------------
    # Exchange authorization code for OAuth tokens
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Check token response
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Access token
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Refresh token
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Save refresh token to .env
    # --------------------------------------------------------

    try:

        set_key(
            str(ENV_FILE),
            "EBAY_REFRESH_TOKEN",
            refresh_token,
        )

        # Reload environment variables so the current
        # application process also knows about the token.
        load_dotenv(
            ENV_FILE,
            override=True
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Refresh token received but could "
                    "not be saved to .env."
                ),
                "error": str(error),
            },
        )

    # --------------------------------------------------------
    # Safe debugging information
    # --------------------------------------------------------

    print(
        "============================================"
    )

    print(
        "eBay OAuth completed successfully"
    )

    print(
        f"Access token received: "
        f"{bool(access_token)}"
    )

    print(
        f"Refresh token received: "
        f"{bool(refresh_token)}"
    )

    print(
        f"Refresh token length: "
        f"{len(refresh_token)}"
    )

    print(
        f"Refresh token saved to: "
        f"{ENV_FILE}"
    )

    print(
        "============================================"
    )

    # ========================================================
    # Common API Headers
    # ========================================================

    api_headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Accept": "application/json",
    }

    # ========================================================
    # Step 3: Traffic Report
    # ========================================================

    traffic_end_date = (
        date.today() - timedelta(days=1)
    )

    traffic_start_date = (
        traffic_end_date - timedelta(days=6)
    )

    traffic_params = {
        "dimension": "DAY",

        "filter": (
            f"marketplace_ids:{{EBAY_US}},"
            f"date_range:"
            f"["
            f"{traffic_start_date.strftime('%Y%m%d')}"
            f".."
            f"{traffic_end_date.strftime('%Y%m%d')}"
            f"]"
        ),

        "metric": (
            "TOTAL_IMPRESSION_TOTAL,"
            "LISTING_VIEWS_TOTAL,"
            "TRANSACTION,"
            "SALES_CONVERSION_RATE"
        ),
    }

    traffic_response = requests.get(
        EBAY_TRAFFIC_URL,
        headers=api_headers,
        params=traffic_params,
        timeout=30,
    )

    if traffic_response.status_code != 200:

        raise HTTPException(
            status_code=traffic_response.status_code,
            detail={
                "message": (
                    "Traffic Report API failed"
                ),
                "request_url": (
                    traffic_response.url
                ),
                "ebay_response": (
                    traffic_response.text
                ),
            },
        )

    traffic_data = traffic_response.json()

    # ========================================================
    # Step 4: Orders
    # ========================================================

    orders_end_date = (
        date.today() - timedelta(days=1)
    )

    orders_start_date = (
        orders_end_date - timedelta(days=30)
    )

    orders_params = {
        "filter": (
            f"creationdate:"
            f"["
            f"{orders_start_date.isoformat()}"
            f"T00:00:00.000Z.."
            f"{orders_end_date.isoformat()}"
            f"T23:59:59.999Z"
            f"]"
        ),

        "limit": 50,

        "offset": 0,
    }

    orders_response = requests.get(
        EBAY_ORDERS_URL,
        headers=api_headers,
        params=orders_params,
        timeout=30,
    )

    if orders_response.status_code != 200:

        raise HTTPException(
            status_code=orders_response.status_code,
            detail={
                "message": (
                    "Orders API failed"
                ),
                "request_url": (
                    orders_response.url
                ),
                "ebay_response": (
                    orders_response.text
                ),
            },
        )

    orders_data = orders_response.json()

    # ========================================================
    # Step 5: Active Listings / Inventory
    # ========================================================

    inventory_params = {
        "limit": 100,
        "offset": 0,
    }

    inventory_response = requests.get(
        EBAY_INVENTORY_URL,
        headers=api_headers,
        params=inventory_params,
        timeout=30,
    )

    if inventory_response.status_code != 200:

        raise HTTPException(
            status_code=inventory_response.status_code,
            detail={
                "message": (
                    "Inventory API failed"
                ),
                "request_url": (
                    inventory_response.url
                ),
                "ebay_response": (
                    inventory_response.text
                ),
            },
        )

    inventory_data = inventory_response.json()

    # ========================================================
    # Step 6: Return All API Data
    # ========================================================

    return {
    "status": (
        "eBay OAuth + Traffic + Orders + "
        "Inventory API successful"
    ),

    "TEMP_REFRESH_TOKEN": refresh_token,

        "traffic_date_range": {
            "start": (
                traffic_start_date.isoformat()
            ),
            "end": (
                traffic_end_date.isoformat()
            ),
        },

        "orders_date_range": {
            "start": (
                orders_start_date.isoformat()
            ),
            "end": (
                orders_end_date.isoformat()
            ),
        },

        "token": {

            "expires_in": (
                token_data.get(
                    "expires_in"
                )
            ),

            "access_token_received": bool(
                token_data.get(
                    "access_token"
                )
            ),

            "refresh_token_received": bool(
                token_data.get(
                    "refresh_token"
                )
            ),
        },

        "traffic_report": traffic_data,

        "orders": orders_data,

        "inventory": inventory_data,
    }