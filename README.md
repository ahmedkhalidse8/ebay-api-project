# eBay Analytics & Business Intelligence Platform

An end-to-end analytics project built around real eBay seller data, demonstrating API integration, Python data ingestion, Snowflake warehousing, dbt transformation, SQL business analysis, and Power BI visualization.

> **Current release: v1.0**
>
> This version focuses on the production-style data pipeline, analytical modeling, SQL analysis, and Power BI dashboard. Controlled experimentation and statistical testing are planned as a future extension.

---

## Project Overview

The objective is to understand eBay seller performance across:

* Sales and revenue
* Orders and units sold
* Listing impressions
* Listing views
* Traffic transactions
* Conversion performance
* Product performance
* Seller payout

The project follows a modern analytics workflow:

**eBay API → FastAPI → Python → Snowflake → dbt → SQL → Power BI**

The project uses the data actually available through the eBay APIs and documents API limitations rather than fabricating unsupported metrics.

---

## Architecture

```text
                    eBay APIs
                        │
                        ▼
                  OAuth 2.0
                        │
                        ▼
                   FastAPI
                        │
                        ▼
                    Vercel
                        │
                        ▼
                Python Extraction
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
          Raw JSON             Transformed CSV
             │                     │
             └──────────┬──────────┘
                        ▼
                    Snowflake
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
             RAW                  dbt
                                   │
                                   ▼
                              Analytical Models
                                   │
                              ┌────┴────┐
                              ▼         ▼
                             SQL    Power BI
```

---

## Data Sources

The project currently retrieves three eBay data domains:

### Traffic

Daily listing traffic metrics including:

* Impressions
* Listing views
* Transactions
* Sales conversion metrics

Current historical extraction covers approximately:

**August 2024 → August 2026**

### Orders

Order and line-item information including:

* Order ID
* Order date
* Product
* Quantity
* Order value
* Delivery cost
* Seller payout
* Order/payment status

Current dataset contains approximately:

* **96 order records**
* **96 unique orders**
* **5 unique products**

### Inventory

Inventory data is also retrieved through the eBay Inventory API.

The current authenticated API response exposes only a limited inventory set, so inventory is treated as an auxiliary data source rather than a central analytical dataset.

---

## Technology Stack

| Layer                    | Technology     |
| ------------------------ | -------------- |
| API                      | eBay REST APIs |
| Authentication           | OAuth 2.0      |
| API application          | FastAPI        |
| Deployment               | Vercel         |
| Data extraction          | Python         |
| Data transformation      | Pandas         |
| Data warehouse           | Snowflake      |
| Transformation framework | dbt            |
| Business analysis        | SQL            |
| Statistical analysis     | Python         |
| Visualization            | Power BI       |
| Version control          | Git / GitHub   |

---

## Repository Structure

```text
ebay-api-project/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── analyze.py
│   └── inspect_orders.py
│
├── processed/
│   ├── daily_sales.csv
│   ├── product_performance.csv
│   ├── traffic.csv
│   └── traffic_analysis.csv
│
├── ebay_analytics/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── sql/
│   │   ├── sales_analysis.sql
│   │   ├── traffic_analysis.sql
│   │   ├── product_analysis.sql
│   │   ├── funnel_analysis.sql
│   │   └── validation.sql
│   └── tests/
│
├── Power BI/
│   └── ebay_analytics_dashboard.pbix
│
└── docs/
    └── images/
```

---

## dbt Data Transformation

The dbt project separates the warehouse into logical transformation layers.

### Staging

* `stg_traffic`
* `stg_orders`
* `stg_inventory`

These models standardize the raw Snowflake data.

### Intermediate

* `int_order_metrics`

This layer derives analytical fields such as revenue-order flags and unit price.

### Marts

* `fct_orders`
* `mart_daily_performance`
* `mart_product_performance`

These models provide business-ready datasets for analysis and Power BI.

---

## Business Analysis

The SQL analysis covers:

### Sales

* Revenue
* Orders
* Units sold
* Average order value
* Seller payout
* Monthly performance
* Revenue trends

### Traffic

* Impressions
* Views
* Traffic transactions
* Impression-to-view rate
* View-to-transaction rate
* Traffic trends

### Product Performance

* Revenue by product
* Units sold by product
* Orders by product
* Revenue contribution
* Average unit price

### Funnel

```text
Impressions
     ↓
Views
     ↓
Traffic Transactions
     ↓
Orders
     ↓
Revenue
```

The funnel analysis is designed to identify where traffic is being generated and where users are failing to progress toward a transaction or order.

---

## Power BI Dashboard

The Power BI dashboard connects to the Snowflake analytical models and presents the business results through interactive reporting.

### Dashboard areas

**Executive Overview**

* Revenue
* Orders
* Average order value
* Impressions
* Views
* Transactions
* Conversion metrics
* Revenue trend
* Orders trend

**Product & Funnel Analysis**

* Product performance
* Revenue contribution
* Orders by product
* Traffic funnel
* Conversion metrics

### Dashboard preview

Screenshots will be added to this section in a future documentation update.

---

## Data Quality

Initial validation includes:

* Row-count validation
* Unique-order validation
* Product-count validation
* Duplicate-date checks
* Date-range validation
* Revenue checks
* Inventory validation
* Source-to-staging reconciliation

dbt models also provide a framework for introducing automated data-quality tests as the project evolves.

---

## API Limitations

The eBay APIs do not expose every business entity required for conventional e-commerce analytics.

Therefore, this project intentionally focuses on the dimensions that can be reliably supported by the available data:

* Traffic
* Orders
* Products
* Revenue
* Seller payout
* Funnel performance

The project does **not** fabricate unsupported customer lifetime value, retention, channel attribution, or other metrics.

Inventory is also treated as an auxiliary source because the current authenticated Inventory API response exposes only a limited inventory set.

---

## Experimentation — Future Extension

A future version of this project will introduce a controlled experimentation framework.

The planned workflow is:

```text
Experiment
    ↓
Control vs Treatment
    ↓
Conversion Measurement
    ↓
Confidence Interval
    ↓
Statistical Test
    ↓
Business Recommendation
```

Historical eBay comparisons will not be presented as A/B tests unless controlled assignment is actually performed.

If synthetic data is used to demonstrate experimentation methodology, it will be explicitly labeled as synthetic.

---

## Key Analytical Objective

The project ultimately aims to answer:

> **What is happening in the eBay business, where is the performance opportunity, and what evidence supports the recommended action?**

The current version establishes the data pipeline and analytical foundation required to answer that question.

---

## Security

Credentials and authentication secrets are stored through environment variables and are intentionally excluded from version control.

Sensitive files such as:

* `.env`
* raw API responses
* local logs
* virtual environments
* dbt build artifacts

are excluded through `.gitignore`.

---

## Project Status

| Component              | Status             |
| ---------------------- | ------------------ |
| Business problem       | ✅ Complete         |
| eBay API integration   | ✅ Complete         |
| OAuth authentication   | ✅ Complete         |
| FastAPI application    | ✅ Complete         |
| Python extraction      | ✅ Complete         |
| Snowflake warehouse    | ✅ Complete         |
| dbt transformations    | ✅ Complete         |
| SQL business analysis  | ✅ Complete         |
| Power BI dashboard     | ✅ Complete         |
| GitHub repository      | ✅ Complete         |
| A/B testing            | ⏳ Future extension |
| Statistical analysis   | ⏳ Future extension |
| Advanced documentation | ⏳ Future extension |

---

## Author

**Ahmed Khalid**

Data Analyst focused on SQL, Python, Power BI, data engineering workflows, and business analytics.
