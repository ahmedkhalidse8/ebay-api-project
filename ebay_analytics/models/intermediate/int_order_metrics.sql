SELECT
    order_id,
    order_date,
    order_status,
    payment_status,
    item_id,
    line_item_id,
    title,
    quantity,
    line_item_price,
    order_total,
    delivery_cost,
    total_due_seller,
    currency,

    CASE
        WHEN total_due_seller > 0 THEN 1
        ELSE 0
    END AS is_revenue_order,

    CASE
        WHEN quantity > 0 THEN line_item_price / quantity
        ELSE 0
    END AS unit_price

FROM {{ ref('stg_orders') }}