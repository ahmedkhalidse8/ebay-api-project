from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"status": "eBay API project is running"}


@app.get("/ebay/marketplace-deletion")
def marketplace_deletion():
    return {"status": "endpoint is working"}