with source as (

    select *
    from ECOMMERCE_ANALYTICS.RAW.TRAFFIC

),

staged as (

    select
        date,
        impressions,
        views,
        transactions,
        conversion_rate

    from source

)

select *
from staged