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

EBAY_AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_TRAFFIC_URL = "https://api.ebay.com/sell/analytics/v1/traffic_report"
EBAY_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order"


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
# Step 1: eBay Login
# ============================================================

@app.get("/ebay/login")
def ebay_login():

    client_id = os.environ["EBAY_CLIENT_ID"]
    ru_name = os.environ["EBAY_RU_NAME"]

    state = secrets.token_urlsafe(32)

    scopes = [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
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

    return RedirectResponse(url=authorization_url)


# ============================================================
# Step 2: OAuth Callback
# ============================================================

@app.get("/ebay/oauth/callback")
def ebay_oauth_callback(
    code: str,
    state: str | None = None
):

    client_id = os.environ["EBAY_CLIENT_ID"]
    client_secret = os.environ["EBAY_CLIENT_SECRET"]
    ru_name = os.environ["EBAY_RU_NAME"]

    # --------------------------------------------------------
    # Exchange authorization code for tokens
    # --------------------------------------------------------

    credentials = f"{client_id}:{client_secret}"

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
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
                "message": "eBay OAuth token exchange failed",
                "ebay_response": token_response.text,
            },
        )

    token_data = token_response.json()

    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=500,
            detail="eBay did not return an access token",
        )

    # ========================================================
    # Step 3: Traffic Report
    # ========================================================

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=6)

    traffic_params = {
        "dimension": "DAY",
        "filter": (
            f"marketplace_ids:{{EBAY_US}},"
            f"date_range:["
            f"{start_date.strftime('%Y%m%d')}.."
            f"{end_date.strftime('%Y%m%d')}"
            f"]"
        ),
        "metric": (
            "TOTAL_IMPRESSION_TOTAL,"
            "LISTING_VIEWS_TOTAL,"
            "TRANSACTION,"
            "SALES_CONVERSION_RATE"
        ),
    }

    api_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
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
                "message": "Traffic Report API failed",
                "request_url": traffic_response.url,
                "ebay_response": traffic_response.text,
            },
        )

    traffic_data = traffic_response.json()

    # ========================================================
    # Step 4: Orders
    # ========================================================

    # eBay Fulfillment API allows order searches using
    # creationdate filters. We request the last 30 days here.
    orders_end = date.today()
    orders_start = orders_end - timedelta(days=30)

    orders_params = {
        "filter": (
            f"creationdate:"
            f"[{orders_start.isoformat()}T00:00:00.000Z.."
            f"{orders_end.isoformat()}T23:59:59.999Z]"
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
                "message": "Orders API failed",
                "request_url": orders_response.url,
                "ebay_response": orders_response.text,
            },
        )

    orders_data = orders_response.json()

    # ========================================================
    # Step 5: Return Everything
    # ========================================================

    return {
        "status": "eBay OAuth + Traffic + Orders API successful",

        "traffic_date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },

        "orders_date_range": {
            "start": orders_start.isoformat(),
            "end": orders_end.isoformat(),
        },

        "token": {
            "expires_in": token_data.get("expires_in"),
            "access_token_received": bool(
                token_data.get("access_token")
            ),
            "refresh_token_received": bool(
                token_data.get("refresh_token")
            ),
        },

        "traffic_report": traffic_data,

        "orders": orders_data,
    }