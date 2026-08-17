import pandas as pd
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "processed"


# ============================================================
# Load processed data
# ============================================================

traffic = pd.read_csv(
    PROCESSED_DIR / "traffic.csv"
)

orders = pd.read_csv(
    PROCESSED_DIR / "orders.csv"
)


# ============================================================
# Basic data preparation
# ============================================================

traffic["date"] = pd.to_datetime(
    traffic["date"]
)

orders["order_date"] = pd.to_datetime(
    orders["order_date"]
)


# ============================================================
# SALES OVERVIEW
# ============================================================

total_orders = orders["order_id"].nunique()

total_units = orders["quantity"].sum()

total_sales = orders["order_total"].sum()

total_seller_proceeds = (
    orders["total_due_seller"].sum()
)

average_order_value = (
    total_sales / total_orders
)


print("\n" + "=" * 60)
print("SALES OVERVIEW")
print("=" * 60)

print(f"Total orders:        {total_orders}")
print(f"Units sold:          {total_units}")
print(f"Customer sales:      ${total_sales:.2f}")
print(f"Seller proceeds:     ${total_seller_proceeds:.2f}")
print(f"Average order value: ${average_order_value:.2f}")


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

product_performance = (
    orders
    .groupby("title")
    .agg(
        orders=("order_id", "nunique"),
        units_sold=("quantity", "sum"),
        sales=("order_total", "sum"),
        seller_proceeds=("total_due_seller", "sum"),
    )
    .reset_index()
)


product_performance["average_order_value"] = (
    product_performance["sales"]
    / product_performance["orders"]
)


product_performance = (
    product_performance
    .sort_values(
        "sales",
        ascending=False
    )
)


print("\n" + "=" * 60)
print("PRODUCT PERFORMANCE")
print("=" * 60)

print(
    product_performance.to_string(
        index=False
    )
)


# ============================================================
# DAILY SALES PERFORMANCE
# ============================================================

daily_sales = (
    orders
    .groupby(
        orders["order_date"].dt.date
    )
    .agg(
        orders=("order_id", "nunique"),
        units_sold=("quantity", "sum"),
        sales=("order_total", "sum"),
        seller_proceeds=(
            "total_due_seller",
            "sum"
        ),
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("DAILY SALES")
print("=" * 60)

print(
    daily_sales.to_string(
        index=False
    )
)


# ============================================================
# TRAFFIC PERFORMANCE
# ============================================================

traffic_summary = traffic.copy()

traffic_summary["sales"] = (
    traffic_summary["transactions"]
)


print("\n" + "=" * 60)
print("TRAFFIC PERFORMANCE")
print("=" * 60)

print(
    traffic_summary.to_string(
        index=False
    )
)


# ============================================================
# TRAFFIC TOTALS
# ============================================================

total_impressions = (
    traffic["impressions"].sum()
)

total_views = (
    traffic["views"].sum()
)

total_transactions = (
    traffic["transactions"].sum()
)

overall_conversion_rate = (
    total_transactions / total_views
    if total_views > 0
    else 0
)


print("\n" + "=" * 60)
print("TRAFFIC SUMMARY")
print("=" * 60)

print(f"Total impressions:       {total_impressions:,}")
print(f"Total listing views:     {total_views:,}")
print(f"Total transactions:      {total_transactions}")
print(
    f"Overall view conversion: "
    f"{overall_conversion_rate:.2%}"
)


# ============================================================
# SALES VS SELLER PROCEEDS
# ============================================================

eBay_deductions = (
    total_sales - total_seller_proceeds
)

deduction_rate = (
    eBay_deductions / total_sales
    if total_sales > 0
    else 0
)


print("\n" + "=" * 60)
print("SELLER PROCEEDS")
print("=" * 60)

print(
    f"Customer sales:      ${total_sales:.2f}"
)

print(
    f"Seller proceeds:     ${total_seller_proceeds:.2f}"
)

print(
    f"Difference:          ${eBay_deductions:.2f}"
)

print(
    f"Effective deduction:  {deduction_rate:.2%}"
)


# ============================================================
# SAVE ANALYSIS OUTPUTS
# ============================================================

product_performance.to_csv(
    PROCESSED_DIR / "product_performance.csv",
    index=False
)

daily_sales.to_csv(
    PROCESSED_DIR / "daily_sales.csv",
    index=False
)

traffic_summary.to_csv(
    PROCESSED_DIR / "traffic_analysis.csv",
    index=False
)


print("\n" + "=" * 60)
print("ANALYSIS COMPLETED")
print("=" * 60)

print(
    "Analysis files saved to:"
)

print(
    PROCESSED_DIR
)