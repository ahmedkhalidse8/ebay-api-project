from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"status": "eBay API project is running"}


@app.get("/ebay/marketplace-deletion")
def marketplace_deletion():
    return {"status": "endpoint is working"}


@app.get("/privacy")
def privacy():
    return {
        "privacy_policy": "SalesAnalytics does not sell, rent, or share user data. "
        "eBay data accessed by this application is used solely for analytics purposes."
    }