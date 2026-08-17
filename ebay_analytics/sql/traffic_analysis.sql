-- ============================================================
-- eBay Traffic Analysis
-- ============================================================


-- ============================================================
-- 1. OVERALL TRAFFIC KPIs
-- ============================================================

SELECT
    SUM(impressions) AS total_impressions,
    SUM(views) AS total_views,
    SUM(transactions) AS total_transactions,
    ROUND(
        SUM(transactions) / NULLIF(SUM(views), 0) * 100,
        2
    ) AS view_to_transaction_conversion
FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_TRAFFIC;


-- ============================================================
-- 2. DAILY TRAFFIC TREND
-- ============================================================

SELECT
    date,
    impressions,
    views,
    transactions,
    ROUND(
        transactions / NULLIF(views, 0) * 100,
        2
    ) AS conversion_rate
FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_TRAFFIC
ORDER BY date;


-- ============================================================
-- 3. MONTHLY TRAFFIC TREND
-- ============================================================

SELECT
    TO_CHAR(DATE_TRUNC('MONTH', date), 'YYYY-MM') AS month,
    SUM(impressions) AS impressions,
    SUM(views) AS views,
    SUM(transactions) AS transactions,
    ROUND(
        SUM(transactions) / NULLIF(SUM(views), 0) * 100,
        2
    ) AS conversion_rate
FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_TRAFFIC
GROUP BY 1
ORDER BY 1;