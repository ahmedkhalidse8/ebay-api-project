-- ============================================================
-- eBay Data Validation
-- ============================================================


-- ============================================================
-- 1. TRAFFIC ROW COUNT AND DATE RANGE
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    MIN(date) AS first_date,
    MAX(date) AS latest_date
FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_TRAFFIC;


-- ============================================================
-- 2. TRAFFIC DUPLICATE DATES
-- ============================================================

SELECT
    date,
    COUNT(*) AS row_count
FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_TRAFFIC
GROUP BY date
HAVING COUNT(*) > 1
ORDER BY row_count DESC;


-- ============================================================
-- 3. ORDER ROW COUNT AND DATE RANGE
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_id) AS unique_orders,
    MIN(order_date) AS first_order,
    MAX(order_date) AS latest_order
FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_ORDERS;


-- ============================================================
-- 4. PRODUCT COUNT
-- ============================================================

SELECT
    COUNT(DISTINCT title) AS unique_products
FROM ECOMMERCE_ANALYTICS.DBT_DEV.STG_ORDERS;


-- ============================================================
-- 5. FACT TABLE VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_id) AS unique_orders,
    SUM(quantity) AS total_units,
    ROUND(SUM(order_total), 2) AS total_revenue
FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS;