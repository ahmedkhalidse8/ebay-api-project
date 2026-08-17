with source as (

    select *
    from ECOMMERCE_ANALYTICS.RAW.ORDERS

),

staged as (

    select
        order_id,
        order_date,
        order_status,
        payment_status,
        seller_id,
        item_id,
        line_item_id,
        title,
        quantity,
        line_item_price,
        order_total,
        delivery_cost,
        total_due_seller,
        currency

    from source

)

select *
from staged