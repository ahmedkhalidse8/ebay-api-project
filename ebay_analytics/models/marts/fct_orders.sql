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
    is_revenue_order,
    unit_price
FROM {{ ref('int_order_metrics') }}