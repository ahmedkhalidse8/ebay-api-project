from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
def home():
    return {"status": "eBay API project is running"}


@app.get("/ebay/marketplace-deletion")
def marketplace_deletion():
    return {"status": "endpoint is working"}


@app.get("/privacy", response_class=HTMLResponse)
def privacy():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SalesAnalytics Privacy Policy</title>
    </head>
    <body>
        <h1>SalesAnalytics Privacy Policy</h1>

        <p>
            SalesAnalytics is an analytics application designed to analyze
            data from the user's eBay seller account.
        </p>

        <h2>Information We Access</h2>
        <p>
            With the user's authorization, SalesAnalytics may access eBay
            account and selling data through the eBay APIs, including sales,
            order, and analytics information.
        </p>

        <h2>How We Use Information</h2>
        <p>
            The information is used solely to provide analytics, reporting,
            business intelligence, and performance analysis for the authorized
            eBay seller account.
        </p>

        <h2>Data Sharing</h2>
        <p>
            SalesAnalytics does not sell, rent, or otherwise share eBay data
            with third parties except where required to operate the application
            or comply with applicable law.
        </p>

        <h2>Data Security</h2>
        <p>
            Authentication credentials and access tokens are treated as
            confidential and are not intentionally exposed publicly.
        </p>

        <h2>Data Retention</h2>
        <p>
            Data is retained only as necessary for the analytics purposes
            described above and may be deleted when it is no longer required.
        </p>

        <h2>Contact</h2>
        <p>
            For questions regarding this privacy policy, contact:
            jdcontact730@gmail.com
        </p>

        <p>Last updated: August 14, 2026</p>
    </body>
    </html>
    """