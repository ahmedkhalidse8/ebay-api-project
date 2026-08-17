import json
import requests

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# Configuration
# ============================================================

VERCEL_DATA_URL = (
    "https://salesanalytics-ahmed.vercel.app/ebay/data"
)


# ============================================================
# Project paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "raw"

RAW_DIR.mkdir(exist_ok=True)


# ============================================================
# Helper: Save JSON
# ============================================================

def save_json(filename, data):

    filepath = RAW_DIR / filename

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved: {filepath}")


# ============================================================
# Step 1: Get data from Vercel
# ============================================================

def get_ebay_data():

    print(
        "Requesting eBay data from Vercel..."
    )

    response = requests.get(
        VERCEL_DATA_URL,
        timeout=60,
    )

    if response.status_code != 200:

        print(
            "--------------------------------------------------"
        )

        print(
            f"Vercel request failed."
        )

        print(
            f"HTTP status: {response.status_code}"
        )

        print(
            f"Response: {response.text}"
        )

        print(
            "--------------------------------------------------"
        )

        response.raise_for_status()

    data = response.json()

    print(
        "eBay data received from Vercel."
    )

    return data


# ============================================================
# Step 2: Save Traffic
# ============================================================

def save_traffic(data):

    traffic = data.get(
        "traffic_report"
    )

    if traffic is None:

        raise RuntimeError(
            "traffic_report was not returned by Vercel."
        )

    save_json(
        "traffic.json",
        traffic
    )


# ============================================================
# Step 3: Save Orders
# ============================================================

def save_orders(data):

    orders = data.get(
        "orders"
    )

    if orders is None:

        raise RuntimeError(
            "orders was not returned by Vercel."
        )

    save_json(
        "orders.json",
        orders
    )


# ============================================================
# Step 4: Save Inventory
# ============================================================

def save_inventory(data):

    inventory = data.get(
        "inventory"
    )

    if inventory is None:

        raise RuntimeError(
            "inventory was not returned by Vercel."
        )

    save_json(
        "inventory.json",
        inventory
    )


# ============================================================
# Step 5: Save extraction metadata
# ============================================================

def save_metadata():

    metadata = {

        "extracted_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "source": (
            "eBay APIs via Vercel"
        ),

        "vercel_endpoint": (
            VERCEL_DATA_URL
        ),

        "datasets": [
            "traffic",
            "orders",
            "inventory",
        ],
    }

    save_json(
        "extraction_metadata.json",
        metadata
    )


# ============================================================
# Main extraction pipeline
# ============================================================

def main():

    print(
        "=================================================="
    )

    print(
        "Starting eBay extraction..."
    )

    print(
        "=================================================="
    )

    # --------------------------------------------------------
    # Ask Vercel for the latest eBay data
    # --------------------------------------------------------

    ebay_data = get_ebay_data()

    # --------------------------------------------------------
    # Save datasets
    # --------------------------------------------------------

    save_traffic(
        ebay_data
    )

    save_orders(
        ebay_data
    )

    save_inventory(
        ebay_data
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    save_metadata()

    print(
        "=================================================="
    )

    print(
        "eBay extraction completed successfully."
    )

    print(
        "=================================================="
    )


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    main()