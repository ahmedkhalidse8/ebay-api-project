SELECT
    title,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS units_sold,
    SUM(order_total) AS revenue,
    SUM(total_due_seller) AS seller_payout,
    AVG(unit_price) AS avg_unit_price
FROM {{ ref('fct_orders') }}
WHERE is_revenue_order = TRUE
GROUP BY title
ORDER BY revenue DESC