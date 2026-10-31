
import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "raw" / "listing_traffic.json"
OUTPUT_FILE = BASE_DIR / "processed" / "listing_image_comparison.csv"

LISTINGS = {
    "227307906290": "Image A",
    "226991664030": "Image B",
}


def main():
    with RAW_FILE.open("r", encoding="utf-8-sig") as file:
        payload = json.load(file)

    report = payload["report"]
    header = report["header"]
    records = report.get("records", [])

    metric_keys = [metric["key"] for metric in header["metrics"]]
    results = {}

    for record in records:
        item_id = str(record["dimensionValues"][0]["value"])

        if item_id not in LISTINGS:
            continue

        values = {
            key: (
                metric["value"]
                if metric.get("applicable", True)
                else None
            )
            for key, metric in zip(metric_keys, record["metricValues"])
        }

        impressions = values.get("TOTAL_IMPRESSION_TOTAL")
        views = values.get("LISTING_VIEWS_TOTAL")
        transactions = values.get("TRANSACTION")
        ebay_conversion = values.get("SALES_CONVERSION_RATE")

        results[item_id] = {
            "listing_label": LISTINGS[item_id],
            "item_id": item_id,
            "start_date": payload["date_range"]["start"],
            "end_date": payload["date_range"]["end"],
            "impressions": impressions,
            "views": views,
            "transactions": transactions,
            "ebay_conversion_rate_pct": (
                float(ebay_conversion) * 100
                if ebay_conversion is not None
                else None
            ),
            "view_rate_pct": (
                float(views) / float(impressions) * 100
                if impressions and views is not None
                else None
            ),
        }
        missing_ids = set(LISTINGS) - set(results)

    if missing_ids:
        raise ValueError(
            f"eBay traffic report is missing listing IDs: {sorted(missing_ids)}"
        )

    for item_id, result in results.items():
        if result["impressions"] is None or result["views"] is None:
            raise ValueError(
                f"Missing impressions or views for listing {item_id}"
            )

        if result["impressions"] < 0 or result["views"] < 0:
            raise ValueError(
                f"Negative traffic metric for listing {item_id}"
            )
    rows = [
        results.get(
            item_id,
            {
                "listing_label": label,
                "item_id": item_id,
                "start_date": payload["date_range"]["start"],
                "end_date": payload["date_range"]["end"],
                "impressions": None,
                "views": None,
                "transactions": None,
                "ebay_conversion_rate_pct": None,
                "view_rate_pct": None,
            },
        )
        for item_id, label in LISTINGS.items()
    ]

    df = pd.DataFrame(rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nLISTING IMAGE COMPARISON")
    print("=" * 70)
    print(df.to_string(index=False))
    print(f"\nSaved comparison to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
