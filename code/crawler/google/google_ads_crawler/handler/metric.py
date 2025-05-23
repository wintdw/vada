# Define all metric fields used in reports
METRIC_FIELDS = {
    # Impression & Position metrics
    "impressions": {"field": "impressions", "type": "integer"},
    "absolute_top_impression_percentage": {
        "field": "absolute_top_impression_percentage",
        "type": "rate",
    },
    "top_impression_percentage": {"field": "top_impression_percentage", "type": "rate"},
    # Cost metrics
    "cost": {"field": "cost_micros", "type": "money"},
    "average_cost": {"field": "average_cost", "type": "money"},
    "average_cpc": {"field": "average_cpc", "type": "money"},
    "average_cpe": {"field": "average_cpe", "type": "money"},
    "average_cpm": {"field": "average_cpm", "type": "money"},
    "average_cpv": {"field": "average_cpv", "type": "money"},
    # Click & Engagement metrics
    "clicks": {"field": "clicks", "type": "integer"},
    "ctr": {"field": "ctr", "type": "rate"},
    "engagements": {"field": "engagements", "type": "integer"},
    "engagement_rate": {"field": "engagement_rate", "type": "rate"},
    "interaction_rate": {"field": "interaction_rate", "type": "rate"},
    "interactions": {"field": "interactions", "type": "integer"},
    # Conversion metrics
    "conversions": {"field": "conversions", "type": "float"},
    "conversions_value": {"field": "conversions_value", "type": "float"},
    "cost_per_conversion": {"field": "cost_per_conversion", "type": "money"},
    "value_per_conversion": {"field": "value_per_conversion", "type": "float"},
    "conversions_from_interactions_rate": {
        "field": "conversions_from_interactions_rate",
        "type": "rate",
    },
    "conversions_by_conversion_date": {
        "field": "conversions_by_conversion_date",
        "type": "float",
    },
    "conversions_value_by_conversion_date": {
        "field": "conversions_value_by_conversion_date",
        "type": "float",
    },
    # All conversion metrics
    "all_conversions": {"field": "all_conversions", "type": "float"},
    "all_conversions_value": {"field": "all_conversions_value", "type": "float"},
    "cost_per_all_conversions": {"field": "cost_per_all_conversions", "type": "money"},
    "value_per_all_conversions": {
        "field": "value_per_all_conversions",
        "type": "float",
    },
    "all_conversions_by_conversion_date": {
        "field": "all_conversions_by_conversion_date",
        "type": "float",
    },
    "all_conversions_value_by_conversion_date": {
        "field": "all_conversions_value_by_conversion_date",
        "type": "float",
    },
    "all_conversions_from_interactions_rate": {
        "field": "all_conversions_from_interactions_rate",
        "type": "rate",
    },
    # Cross-device metrics
    "cross_device_conversions": {"field": "cross_device_conversions", "type": "float"},
    "cross_device_conversions_value_micros": {
        "field": "cross_device_conversions_value_micros",
        "type": "money",
    },
    # Current model metrics
    "current_model_attributed_conversions": {
        "field": "current_model_attributed_conversions",
        "type": "float",
    },
    "current_model_attributed_conversions_value": {
        "field": "current_model_attributed_conversions_value",
        "type": "float",
    },
    "cost_per_current_model_attributed_conversion": {
        "field": "cost_per_current_model_attributed_conversion",
        "type": "money",
    },
    "value_per_current_model_attributed_conversion": {
        "field": "value_per_current_model_attributed_conversion",
        "type": "float",
    },
    # Video metrics
    "video_views": {"field": "video_views", "type": "integer"},
    "video_view_rate": {"field": "video_view_rate", "type": "rate"},
    "video_quartile_p25_rate": {"field": "video_quartile_p25_rate", "type": "rate"},
    "video_quartile_p50_rate": {"field": "video_quartile_p50_rate", "type": "rate"},
    "video_quartile_p75_rate": {"field": "video_quartile_p75_rate", "type": "rate"},
    "video_quartile_p100_rate": {"field": "video_quartile_p100_rate", "type": "rate"},
    # Active View metrics
    "active_view_impressions": {"field": "active_view_impressions", "type": "integer"},
    "active_view_cpm": {"field": "active_view_cpm", "type": "money"},
    "active_view_ctr": {"field": "active_view_ctr", "type": "rate"},
    "active_view_viewability": {"field": "active_view_viewability", "type": "rate"},
    "active_view_measurable_impressions": {
        "field": "active_view_measurable_impressions",
        "type": "integer",
    },
    "active_view_measurable_cost_micros": {
        "field": "active_view_measurable_cost_micros",
        "type": "money",
    },
    "active_view_measurability": {"field": "active_view_measurability", "type": "rate"},
    # Gmail specific metrics
    "gmail_forwards": {"field": "gmail_forwards", "type": "integer"},
    "gmail_saves": {"field": "gmail_saves", "type": "integer"},
    "gmail_secondary_clicks": {"field": "gmail_secondary_clicks", "type": "integer"},
    # Website metrics
    "bounce_rate": {"field": "bounce_rate", "type": "rate"},
    "average_page_views": {"field": "average_page_views", "type": "float"},
    "average_time_on_site": {"field": "average_time_on_site", "type": "float"},
    "percent_new_visitors": {"field": "percent_new_visitors", "type": "rate"},
    # Revenue & profit metrics
    "revenue_micros": {"field": "revenue_micros", "type": "money"},
    "cost_of_goods_sold_micros": {
        "field": "cost_of_goods_sold_micros",
        "type": "money",
    },
    "gross_profit_micros": {"field": "gross_profit_micros", "type": "money"},
    "gross_profit_margin": {"field": "gross_profit_margin", "type": "rate"},
    # Customer metrics
    "average_order_value_micros": {
        "field": "average_order_value_micros",
        "type": "money",
    },
    "average_cart_size": {"field": "average_cart_size", "type": "float"},
    "orders": {"field": "orders", "type": "integer"},
    "units_sold": {"field": "units_sold", "type": "integer"},
    # Cross-sell metrics
    "cross_sell_cost_of_goods_sold_micros": {
        "field": "cross_sell_cost_of_goods_sold_micros",
        "type": "money",
    },
    "cross_sell_gross_profit_micros": {
        "field": "cross_sell_gross_profit_micros",
        "type": "money",
    },
    "cross_sell_revenue_micros": {
        "field": "cross_sell_revenue_micros",
        "type": "money",
    },
    "cross_sell_units_sold": {"field": "cross_sell_units_sold", "type": "integer"},
    # Lead metrics
    "lead_cost_of_goods_sold_micros": {
        "field": "lead_cost_of_goods_sold_micros",
        "type": "money",
    },
    "lead_gross_profit_micros": {"field": "lead_gross_profit_micros", "type": "money"},
    "lead_revenue_micros": {"field": "lead_revenue_micros", "type": "money"},
    "lead_units_sold": {"field": "lead_units_sold", "type": "integer"},
    # Customer lifetime value metrics
    "new_customer_lifetime_value": {
        "field": "new_customer_lifetime_value",
        "type": "float",
    },
    "all_new_customer_lifetime_value": {
        "field": "all_new_customer_lifetime_value",
        "type": "float",
    },
    # View-through conversions
    "view_through_conversions": {"field": "view_through_conversions", "type": "float"},
}
