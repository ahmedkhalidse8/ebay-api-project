-- ============================================================
-- eBay Funnel Analysis
-- ============================================================


-- ============================================================
-- 1. OVERALL FUNNEL
-- ============================================================

WITH traffic AS (

    SELECT
        SUM(impressions) AS impressions,
        SUM(views) AS views,
        SUM(transactions) AS transactions
    FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_TRAFFIC

),

orders AS (

    SELECT
        COUNT(DISTINCT order_id) AS orders,
        SUM(quantity) AS units_sold,
        ROUND(SUM(order_total), 2) AS revenue
    FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS

)

SELECT
    impressions,
    views,
    transactions,
    orders,
    units_sold,
    revenue,

    ROUND(
        views / NULLIF(impressions, 0) * 100,
        2
    ) AS impression_to_view_rate,

    ROUND(
        transactions / NULLIF(views, 0) * 100,
        2
    ) AS view_to_transaction_rate,

    ROUND(
        orders / NULLIF(transactions, 0) * 100,
        2
    ) AS transaction_to_order_rate

FROM traffic
CROSS JOIN orders;


-- ============================================================
-- 2. MONTHLY FUNNEL
-- ============================================================

WITH traffic_monthly AS (

    SELECT
        DATE_TRUNC('MONTH', date) AS month,
        SUM(impressions) AS impressions,
        SUM(views) AS views,
        SUM(transactions) AS transactions
    FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_TRAFFIC
    GROUP BY 1

),

orders_monthly AS (

    SELECT
        DATE_TRUNC('MONTH', order_date) AS month,
        COUNT(DISTINCT order_id) AS orders,
        SUM(quantity) AS units_sold,
        ROUND(SUM(order_total), 2) AS revenue
    FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS
    GROUP BY 1

)

SELECT
    t.month,
    t.impressions,
    t.views,
    t.transactions,
    COALESCE(o.orders, 0) AS orders,
    COALESCE(o.units_sold, 0) AS units_sold,
    COALESCE(o.revenue, 0) AS revenue,

    ROUND(
        t.views / NULLIF(t.impressions, 0) * 100,
        2
    ) AS impression_to_view_rate,

    ROUND(
        t.transactions / NULLIF(t.views, 0) * 100,
        2
    ) AS view_to_transaction_rate

FROM traffic_monthly t
LEFT JOIN orders_monthly o
    ON t.month = o.month
ORDER BY t.month;