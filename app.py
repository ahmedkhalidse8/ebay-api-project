import os
import base64
import requests

from datetime import date, timedelta

from fastapi import FastAPI, HTTPException


app = FastAPI()


# ============================================================
# eBay API URLs
# ============================================================

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
# Step 1: Get Access Token Using Refresh Token
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

    token_headers = {
        "Content-Type": (
            "application/x-www-form-urlencoded"
        ),
        "Authorization": (
            f"Basic {encoded_credentials}"
        ),
    }

    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    token_response = requests.post(
        EBAY_TOKEN_URL,
        headers=token_headers,
        data=token_data,
        timeout=30,
    )

    if token_response.status_code != 200:

        raise HTTPException(
            status_code=token_response.status_code,
            detail={
                "message": (
                    "eBay access token refresh failed"
                ),
                "ebay_response": (
                    token_response.text
                ),
            },
        )

    token_json = token_response.json()

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "eBay did not return an access token"
                ),
                "ebay_response": token_json,
            },
        )

    return access_token


# ============================================================
# Step 2: Test eBay Authentication
# ============================================================

@app.get("/ebay/test-auth")
def test_auth():

    access_token = get_access_token()

    return {
        "status": "eBay authentication successful",
        "access_token_received": bool(
            access_token
        ),
    }


# ============================================================
# Step 3: Traffic Report
# ============================================================

def get_traffic_report(access_token):

    traffic_end_date = (
        date.today() - timedelta(days=1)
    )

    traffic_start_date = (
        traffic_end_date - timedelta(days=6)
    )

    traffic_headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Accept": "application/json",
    }

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

    response = requests.get(
        EBAY_TRAFFIC_URL,
        headers=traffic_headers,
        params=traffic_params,
        timeout=30,
    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": (
                    "Traffic Report API failed"
                ),
                "request_url": response.url,
                "ebay_response": response.text,
            },
        )

    return {
        "date_range": {
            "start": (
                traffic_start_date.isoformat()
            ),
            "end": (
                traffic_end_date.isoformat()
            ),
        },
        "data": response.json(),
    }


# ============================================================
# Step 4: Orders
# ============================================================

def get_orders(access_token):

    orders_end_date = (
        date.today() - timedelta(days=1)
    )

    orders_start_date = (
        orders_end_date - timedelta(days=30)
    )

    orders_headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Accept": "application/json",
    }

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

    response = requests.get(
        EBAY_ORDERS_URL,
        headers=orders_headers,
        params=orders_params,
        timeout=30,
    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": (
                    "Orders API failed"
                ),
                "request_url": response.url,
                "ebay_response": response.text,
            },
        )

    return {
        "date_range": {
            "start": (
                orders_start_date.isoformat()
            ),
            "end": (
                orders_end_date.isoformat()
            ),
        },
        "data": response.json(),
    }


# ============================================================
# Step 5: Inventory
# ============================================================

def get_inventory(access_token):

    inventory_headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Accept": "application/json",
    }

    inventory_params = {
        "limit": 100,
        "offset": 0,
    }

    response = requests.get(
        EBAY_INVENTORY_URL,
        headers=inventory_headers,
        params=inventory_params,
        timeout=30,
    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": (
                    "Inventory API failed"
                ),
                "request_url": response.url,
                "ebay_response": response.text,
            },
        )

    return response.json()


# ============================================================
# Step 6: Complete eBay Data Extraction
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