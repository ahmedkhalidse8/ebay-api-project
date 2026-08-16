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
# Marketplace Deletion
# ============================================================

@app.get("/ebay/marketplace-deletion")
def marketplace_deletion():

    return {
        "status": "endpoint is working"
    }


# ============================================================
# Debug Environment
# ============================================================

@app.get("/debug/env")
def debug_env():

    return {
        "client_id_present": bool(
            os.getenv("EBAY_CLIENT_ID")
        ),

        "client_secret_present": bool(
            os.getenv("EBAY_CLIENT_SECRET")
        ),

        "ru_name_present": bool(
            os.getenv("EBAY_RU_NAME")
        ),

        "refresh_token_present": bool(
            os.getenv("EBAY_REFRESH_TOKEN")
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

        "https://api.ebay.com/oauth/api_scope/"
        "sell.analytics.readonly",

        "https://api.ebay.com/oauth/api_scope/"
        "sell.account.readonly",

        "https://api.ebay.com/oauth/api_scope/"
        "sell.fulfillment.readonly",

        "https://api.ebay.com/oauth/api_scope/"
        "sell.inventory.readonly",
    ]

    authorization_url = (
        f"{EBAY_AUTH_URL}"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={ru_name}"
        f"&scope={' '.join(scopes)}"
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

    headers = {
        "Content-Type": (
            "application/x-www-form-urlencoded"
        ),

        "Authorization": (
            f"Basic {encoded_credentials}"
        ),
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": ru_name,
    }

    response = requests.post(
        EBAY_TOKEN_URL,
        headers=headers,
        data=data,
        timeout=30,
    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "eBay OAuth token exchange failed",
                "ebay_response": response.text,
            },
        )

    token_data = response.json()

    refresh_token = token_data.get(
        "refresh_token"
    )

    if not refresh_token:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "eBay did not return a refresh token."
                )
            },
        )

    return {
        "status": "OAuth successful",

        "message": (
            "Copy this refresh token and add it "
            "to the EBAY_REFRESH_TOKEN environment "
            "variable in Vercel."
        ),

        "refresh_token": refresh_token,

        "expires_in": token_data.get(
            "refresh_token_expires_in"
        ),
    }


# ============================================================
# Step 3: Get Fresh Access Token
# ============================================================

def get_access_token():

    client_id = get_env("EBAY_CLIENT_ID")
    client_secret = get_env("EBAY_CLIENT_SECRET")
    refresh_token = get_env("EBAY_REFRESH_TOKEN")

    credentials = (
        f"{client_id}:{client_secret}"
    )

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Content-Type": (
            "application/x-www-form-urlencoded"
        ),

        "Authorization": (
            f"Basic {encoded_credentials}"
        ),
    }

    data = {
        "grant_type": "refresh_token",

        "refresh_token": refresh_token,
    }

    response = requests.post(
        EBAY_TOKEN_URL,
        headers=headers,
        data=data,
        timeout=30,
    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": (
                    "eBay access token refresh failed"
                ),

                "ebay_response": response.text,
            },
        )

    token_data = response.json()

    access_token = token_data.get(
        "access_token"
    )

    if not access_token:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "eBay did not return an access token."
                )
            },
        )

    return access_token


# ============================================================
# Step 4: Test Authentication
# ============================================================

@app.get("/ebay/test-auth")
def test_auth():

    access_token = get_access_token()

    return {
        "status": (
            "eBay authentication successful"
        ),

        "access_token_received": bool(
            access_token
        ),
    }


# ============================================================
# Step 5: Traffic Report
# ============================================================

def get_traffic_report(access_token):

    end_date = date.today() - timedelta(days=1)

    start_date = end_date - timedelta(days=730)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    all_records = []

    current_start = start_date

    while current_start <= end_date:

        current_end = min(
            current_start + timedelta(days=89),
            end_date
        )

        params = {
            "dimension": "DAY",

            "filter": (
                f"marketplace_ids:{{EBAY_US}},"
                f"date_range:"
                f"["
                f"{current_start.strftime('%Y%m%d')}"
                f".."
                f"{current_end.strftime('%Y%m%d')}"
                f"]"
            ),

            "metric": (
                "TOTAL_IMPRESSION_TOTAL,"
                "LISTING_VIEWS_TOTAL,"
                "TRANSACTION,"
                "SALES_CONVERSION_RATE"
            ),
        }

        response = requests.get(
            EBAY_TRAFFIC_URL,
            headers=headers,
            params=params,
            timeout=30,
        )

        if response.status_code != 200:

            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "message": "Traffic Report API failed",

                    "date_range": (
                        f"{current_start.isoformat()} "
                        f"to {current_end.isoformat()}"
                    ),

                    "ebay_response": response.text,
                },
            )

        data = response.json()

        records = data.get("records", [])

        all_records.extend(records)

        print(
            f"Traffic retrieved: "
            f"{current_start} → {current_end} "
            f"({len(records)} records)"
        )

        current_start = current_end + timedelta(days=1)

    return {
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },

        "records": all_records,
    }


# ============================================================
# Step 6: Orders
# ============================================================

def get_orders(access_token):

    end_date = (
        date.today() - timedelta(days=1)
    )

    start_date = (
        end_date - timedelta(days=30)
    )

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),

        "Accept": "application/json",
    }

    params = {

        "filter": (
            f"creationdate:"
            f"["
            f"{start_date.isoformat()}"
            f"T00:00:00.000Z.."
            f"{end_date.isoformat()}"
            f"T23:59:59.999Z"
            f"]"
        ),

        "limit": 50,

        "offset": 0,
    }

    response = requests.get(
        EBAY_ORDERS_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": (
                    "Orders API failed"
                ),

                "ebay_response": response.text,
            },
        )

    return {
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },

        "data": response.json(),
    }


# ============================================================
# Step 7: Inventory
# ============================================================

def get_inventory(access_token):

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),

        "Accept": "application/json",
    }

    params = {
        "limit": 100,
        "offset": 0,
    }

    response = requests.get(
        EBAY_INVENTORY_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": (
                    "Inventory API failed"
                ),

                "ebay_response": response.text,
            },
        )

    return response.json()


# ============================================================
# Step 8: Complete eBay Data Extraction
# ============================================================

@app.get("/ebay/data")
def ebay_data():

    access_token = get_access_token()

    traffic = get_traffic_report(
        access_token
    )

    orders = get_orders(
        access_token
    )

    inventory = get_inventory(
        access_token
    )

    return {

        "status": (
            "eBay data extraction successful"
        ),

        "traffic_report": traffic,

        "orders": orders,

        "inventory": inventory,
    }