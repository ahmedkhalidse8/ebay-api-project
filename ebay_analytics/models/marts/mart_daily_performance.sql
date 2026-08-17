WITH orders AS (

    SELECT
        DATE(order_date) AS order_date,
        COUNT(DISTINCT order_id) AS orders,
        SUM(quantity) AS units_sold,
        SUM(order_total) AS revenue,
        SUM(delivery_cost) AS delivery_cost,
        SUM(total_due_seller) AS seller_payout
    FROM {{ ref('fct_orders') }}
    WHERE is_revenue_order = TRUE
    GROUP BY 1

),

traffic AS (

    SELECT
        date,
        SUM(impressions) AS impressions,
        SUM(views) AS views,
        SUM(transactions) AS traffic_transactions
    FROM {{ ref('stg_traffic') }}
    GROUP BY 1

)

SELECT
    COALESCE(o.order_date, t.date) AS date,

    COALESCE(o.orders, 0) AS orders,
    COALESCE(o.units_sold, 0) AS units_sold,
    COALESCE(o.revenue, 0) AS revenue,
    COALESCE(o.delivery_cost, 0) AS delivery_cost,
    COALESCE(o.seller_payout, 0) AS seller_payout,

    COALESCE(t.impressions, 0) AS impressions,
    COALESCE(t.views, 0) AS views,
    COALESCE(t.traffic_transactions, 0) AS traffic_transactions,

    CASE
        WHEN COALESCE(t.views, 0) > 0
        THEN o.orders / t.views
        ELSE 0
    END AS view_to_order_rate,

    CASE
        WHEN COALESCE(o.orders, 0) > 0
        THEN o.revenue / o.orders
        ELSE 0
    END AS average_order_value

FROM orders o
FULL OUTER JOIN traffic t
    ON o.order_date = t.date