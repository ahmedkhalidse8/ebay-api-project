import json
from pathlib import Path

import pandas as pd


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"

PROCESSED_DIR.mkdir(exist_ok=True)


# ============================================================
# Helper: load JSON
# ============================================================

def load_json(filename):

    filepath = RAW_DIR / filename

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# Helper: save CSV
# ============================================================

def save_csv(filename, dataframe):

    filepath = PROCESSED_DIR / filename

    dataframe.to_csv(
        filepath,
        index=False,
        encoding="utf-8"
    )

    print(f"Saved: {filepath}")
    print(f"Rows: {len(dataframe)}")
    print()


# ============================================================
# 1. Transform Traffic
# ============================================================

def transform_traffic():

    print("=" * 60)
    print("Transforming traffic data...")
    print("=" * 60)

    raw = load_json("traffic.json")

    records = raw["records"]

    rows = []

    for record in records:

        date_value = record["dimensionValues"][0]["value"]

        metrics = record["metricValues"]

        impressions = metrics[0]["value"]
        views = metrics[1]["value"]
        transactions = metrics[2]["value"]
        conversion_rate = metrics[3]["value"]

        rows.append(
            {
                "date": pd.to_datetime(
                    date_value,
                    format="%Y%m%d"
                ).date(),

                "impressions": impressions,

                "views": views,

                "transactions": transactions,

                "conversion_rate": conversion_rate,
            }
        )

    df = pd.DataFrame(rows)

    df = df.sort_values("date")

    save_csv(
        "traffic.csv",
        df
    )

    return df


# ============================================================
# 2. Transform Orders
# ============================================================

def transform_orders():

    print("=" * 60)
    print("Transforming orders data...")
    print("=" * 60)

    raw = load_json("orders.json")

    orders = raw.get(
        "orders",
        []
    )

    rows = []

    for order in orders:

        pricing = order.get(
            "pricingSummary",
            {}
        )

        payment = order.get(
            "paymentSummary",
            {}
        )

        line_items = order.get(
            "lineItems",
            []
        )

        total_due_seller = (
            payment
            .get("totalDueSeller", {})
            .get("value")
        )

        order_total = (
            pricing
            .get("total", {})
            .get("value")
        )

        delivery_cost = (
            pricing
            .get("deliveryCost", {})
            .get("value")
        )

        for item in line_items:

            line_item_cost = (
                item
                .get("lineItemCost", {})
                .get("value")
            )

            quantity = item.get(
                "quantity",
                0
            )

            rows.append(
                {
                    "order_id": order.get(
                        "orderId"
                    ),

                    "order_date": order.get(
                        "creationDate"
                    ),

                    "order_status": order.get(
                        "orderFulfillmentStatus"
                    ),

                    "payment_status": order.get(
                        "orderPaymentStatus"
                    ),

                    "seller_id": order.get(
                        "sellerId"
                    ),

                    "item_id": item.get(
                        "legacyItemId"
                    ),

                    "line_item_id": item.get(
                        "lineItemId"
                    ),

                    "title": item.get(
                        "title"
                    ),

                    "quantity": quantity,

                    "line_item_price": line_item_cost,

                    "order_total": order_total,

                    "delivery_cost": delivery_cost,

                    "total_due_seller": total_due_seller,

                    "currency": (
                        pricing
                        .get("total", {})
                        .get("currency")
                    ),
                }
            )

    df = pd.DataFrame(rows)

    if not df.empty:

        df["order_date"] = pd.to_datetime(
            df["order_date"],
            errors="coerce"
        )

        numeric_columns = [
            "quantity",
            "line_item_price",
            "order_total",
            "delivery_cost",
            "total_due_seller",
        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df = df.sort_values(
            "order_date"
        )

    save_csv(
        "orders.csv",
        df
    )

    return df


# ============================================================
# 3. Transform Buyer Analysis
# ============================================================

def transform_buyer_analysis():

    print("=" * 60)
    print("Transforming buyer analysis...")
    print("=" * 60)

    raw = load_json("orders.json")
    orders = raw.get("orders", [])

    rows = []

    for order in orders:

        buyer = order.get("buyer", {})
        username = buyer.get("username")

        if not username:
            continue

        pricing = order.get("pricingSummary", {})
        payment = order.get("paymentSummary", {})

        rows.append({
            "buyer_key": username,
            "order_id": order.get("orderId"),
            "order_date": order.get("creationDate"),
            "order_total": (
                pricing.get("total", {}).get("value")
            ),
            "seller_proceeds": (
                payment.get("totalDueSeller", {}).get("value")
            ),
        })

    df = pd.DataFrame(rows)

    if df.empty:
        print("No buyer records available.")
        return df

    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce", utc=True
    )

    for column in ["order_total", "seller_proceeds"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Stable pseudonymous IDs; raw usernames are never exported.
    buyer_ids = {
        username: f"BUYER_{index:03d}"
        for index, username in enumerate(
            sorted(df["buyer_key"].unique()), start=1
        )
    }

    df["buyer_id"] = df["buyer_key"].map(buyer_ids)

    buyer_summary = (
        df.groupby("buyer_id")
        .agg(
            order_count=("order_id", "nunique"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
            customer_sales=("order_total", "sum"),
            seller_proceeds=("seller_proceeds", "sum"),
        )
        .reset_index()
    )

    buyer_summary["repeat_buyer"] = (
        buyer_summary["order_count"] > 1
    )

    buyer_summary = buyer_summary.drop(
        columns=[], errors="ignore"
    )

    save_csv("buyer_analysis.csv", buyer_summary)

    print("Unique buyers:", len(buyer_summary))
    print("Repeat buyers:", int(buyer_summary["repeat_buyer"].sum()))

    return buyer_summary

# ============================================================
# 3. Transform Inventory
# ============================================================

def transform_inventory():

    print("=" * 60)
    print("Transforming inventory data...")
    print("=" * 60)

    raw = load_json("inventory.json")

    inventory_items = raw.get(
        "inventoryItems",
        []
    )

    rows = []

    for item in inventory_items:

        product = item.get(
            "product",
            {}
        )

        availability = item.get(
            "availability",
            {}
        )

        ship_to_location = (
            availability
            .get("shipToLocationAvailability", {})
        )

        rows.append(
            {
                "sku": item.get(
                    "sku"
                ),

                "title": product.get(
                    "title"
                ),

                "description": product.get(
                    "description"
                ),

                "quantity": ship_to_location.get(
                    "quantity"
                ),

                "condition": item.get(
                    "condition"
                ),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:

        df["quantity"] = pd.to_numeric(
            df["quantity"],
            errors="coerce"
        )

    save_csv(
        "inventory.csv",
        df
    )

    return df


# ============================================================
# 4. Transformation Pipeline
# ============================================================

def main():

    print()
    print("=" * 60)
    print("STARTING eBAY TRANSFORMATION")
    print("=" * 60)
    print()

    traffic_df = transform_traffic()

    orders_df = transform_orders()
    buyer_df = transform_buyer_analysis()
    inventory_df = transform_inventory()

    print("=" * 60)
    print("TRANSFORMATION COMPLETED")
    print("=" * 60)
    print()

    print("Traffic:")
    print(traffic_df)

    print()
    print("Orders:")
    print(orders_df.head())

    print()
    print("Inventory:")
    print(inventory_df.head())

    print()
    print("Processed files created:")
    print(PROCESSED_DIR)


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    main()