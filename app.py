import os
import base64
import secrets
import requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI()


EBAY_AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"


@app.get("/")
def home():
    return {"status": "SalesAnalytics API is running"}


@app.get("/ebay/marketplace-deletion")
def marketplace_deletion():
    return {"status": "endpoint is working"}


@app.get("/ebay/login")
def ebay_login():
    client_id = os.environ["EBAY_CLIENT_ID"]
    ru_name = os.environ["EBAY_RU_NAME"]

    state = secrets.token_urlsafe(32)

    scopes = [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
        "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
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


@app.get("/ebay/oauth/callback")
def ebay_oauth_callback(code: str, state: str | None = None):
    client_id = os.environ["EBAY_CLIENT_ID"]
    client_secret = os.environ["EBAY_CLIENT_SECRET"]
    ru_name = os.environ["EBAY_RU_NAME"]

    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
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
            detail=response.text,
        )

    token_data = response.json()

    return {
        "status": "OAuth token exchange successful",
        "expires_in": token_data.get("expires_in"),
        "refresh_token_received": bool(
            token_data.get("refresh_token")
        ),
        "access_token_received": bool(
            token_data.get("access_token")
        ),
    }