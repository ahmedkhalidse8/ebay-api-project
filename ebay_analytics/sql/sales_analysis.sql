-- ============================================================
-- eBay Sales Analysis
-- ============================================================
--
-- Purpose:
-- Analyze sales performance using the dbt orders fact table.
--
-- Business questions:
-- 1. What are the overall sales KPIs?
-- 2. How are sales changing over time?
-- 3. Which products perform best?
-- 4. How concentrated is revenue across products?
-- 5. Which products sell the most units?
-- 6. What does the order-value distribution look like?
--
-- Source:
-- ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS
-- ============================================================


-- ============================================================
-- 1. OVERALL SALES KPIs
-- ============================================================

SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS units_sold,
    ROUND(SUM(order_total), 2) AS total_revenue,
    ROUND(SUM(total_due_seller), 2) AS total_seller_payout,
    ROUND(
        SUM(order_total) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_order_value
FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS;


-- ============================================================
-- 2. MONTHLY SALES TREND
-- ============================================================

SELECT
    TO_CHAR(
        DATE_TRUNC('MONTH', order_date),
        'YYYY-MM'
    ) AS month,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS units_sold,
    ROUND(SUM(order_total), 2) AS revenue,
    ROUND(SUM(total_due_seller), 2) AS seller_payout,
    ROUND(
        SUM(order_total) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_order_value
FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- 3. PRODUCT PERFORMANCE
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
-- 4. REVENUE CONTRIBUTION BY PRODUCT
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
-- 5. TOP PRODUCTS BY UNITS SOLD
-- ============================================================

SELECT
    title,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(order_total), 2) AS revenue
FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS
GROUP BY title
ORDER BY units_sold DESC;


-- ============================================================
-- 6. ORDER VALUE DISTRIBUTION
-- ============================================================

SELECT
    MIN(order_total) AS minimum_order_value,
    ROUND(AVG(order_total), 2) AS average_order_value,
    MEDIAN(order_total) AS median_order_value,
    MAX(order_total) AS maximum_order_value
FROM ECOMMERCE_ANALYTICS.DBT_DEV.FCT_ORDERS;