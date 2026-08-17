-- ============================================================
-- eBay Product Analysis
-- ============================================================


-- ============================================================
-- 1. PRODUCT PERFORMANCE
-- ============================================================

SELECT
    title,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS units_sold,
    ROUND(SUM(order_total), 2) AS revenue,
    ROUND(SUM(total_due_seller), 2) AS seller_payout,
    ROUND(
        SUM(order_total) / NULLIF(SUM(quantity), 0),
        2
    ) AS average_unit_price
FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS
GROUP BY title
ORDER BY revenue DESC;


-- ============================================================
-- 2. REVENUE CONTRIBUTION BY PRODUCT
-- ============================================================

WITH product_sales AS (

    SELECT
        title,
        SUM(order_total) AS revenue
    FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS
    GROUP BY title

)

SELECT
    title,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        revenue / NULLIF(SUM(revenue) OVER (), 0) * 100,
        2
    ) AS revenue_percentage
FROM product_sales
ORDER BY revenue DESC;


-- ============================================================
-- 3. TOP PRODUCTS BY UNITS SOLD
-- ============================================================

SELECT
    title,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(order_total), 2) AS revenue
FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS
GROUP BY title
ORDER BY units_sold DESC;