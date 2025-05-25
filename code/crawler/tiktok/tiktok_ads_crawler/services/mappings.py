from typing import Dict
import json

from tools import put
from tools.settings import settings

async def create_crm_mappings(
    index_name: str, vada_uid: str, account_email: str
) -> Dict:
    """Copy CRM mappings from the mappings service
    Args:
        index_name: Name of the index to copy mappings for
        vada_uid: Vada user ID
        account_email: Account email of the Google account - for friendly name
    """

    async def create_crm_mappings_handler(
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mappings: Dict,
        id_field: str = "",
        agg_field: str = "",
        time_field: str = "",
    ) -> Dict:
        url = f"{settings.MAPPINGS_BASE_URL}/crm/mappings"

        payload = {
            "user_id": user_id,
            "index_name": index_name,
            "index_friendly_name": index_friendly_name,
            "mappings": mappings,
            "id_field": id_field,
            "agg_field": agg_field,
            "time_field": time_field,
        }
        return await put(url, json=payload)

    response = await create_crm_mappings_handler(
        user_id=vada_uid,
        index_name=index_name,
        index_friendly_name=f"Tiktok Ads {account_email}",
        mappings=json.loads('''
        {
            "_doc": {
                "dynamic": "true",
                "dynamic_date_formats": [
                "strict_date_optional_time",
                "basic_date",
                "basic_date_time",
                "basic_date_time_no_millis",
                "yyyy/MM/dd HH:mm:ss"
                ],
                "properties": {
                "ad": {
                    "properties": {
                    "ad_format": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "ad_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "ad_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "ad_ref_pixel_id": {
                        "type": "long"
                    },
                    "ad_text": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "adgroup_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "adgroup_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "advertiser_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "aigc_disclosure_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "app_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "auto_message_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "avatar_icon_web_uri": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "brand_safety_postbid_partner": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "branded_content_disabled": {
                        "type": "boolean"
                    },
                    "call_to_action": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "call_to_action_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "card_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "catalog_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "click_tracking_url": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "create_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "creative_authorized": {
                        "type": "boolean"
                    },
                    "creative_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "dark_post_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "deeplink": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "deeplink_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "display_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "dynamic_destination": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "dynamic_format": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "fallback_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "identity_authorized_bc_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "identity_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "identity_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "image_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "impression_tracking_url": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "is_aco": {
                        "type": "boolean"
                    },
                    "is_new_structure": {
                        "type": "boolean"
                    },
                    "item_group_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "landing_page_url": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "modify_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "music_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "operation_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "optimization_event": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "page_id": {
                        "type": "long"
                    },
                    "playable_url": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "product_set_id": {
                        "type": "long"
                    },
                    "product_specific_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "profile_image_url": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "promotional_music_disabled": {
                        "type": "boolean"
                    },
                    "secondary_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "shopping_ads_deeplink_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "shopping_ads_fallback_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "shopping_ads_video_package_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "sku_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "tiktok_item_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "tracking_pixel_id": {
                        "type": "long"
                    },
                    "utm_params": {
                        "type": "nested",
                        "properties": {
                        "key": {
                            "type": "text",
                            "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                            }
                        },
                        "value": {
                            "type": "text",
                            "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                            }
                        }
                        }
                    },
                    "vast_moat_enabled": {
                        "type": "boolean"
                    },
                    "vertical_video_strategy": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "video_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "viewability_postbid_partner": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    }
                    }
                },
                "ad_id": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "eager_global_ordinals": true,
                        "ignore_above": 256
                    }
                    }
                },
                "adgroup": {
                    "properties": {
                    "actions": {
                        "properties": {
                        "action_category_ids": {
                            "type": "text",
                            "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                            }
                        },
                        "action_period": {
                            "type": "long"
                        },
                        "action_scene": {
                            "type": "text",
                            "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                            }
                        },
                        "video_user_actions": {
                            "type": "text",
                            "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                            }
                        }
                        }
                    },
                    "adgroup_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "adgroup_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "advertiser_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "age_groups": {
                        "type": "text"
                    },
                    "attribution_event_count": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "audience_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "auto_targeting_enabled": {
                        "type": "boolean"
                    },
                    "bid_display_mode": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "bid_price": {
                        "type": "float"
                    },
                    "bid_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "billing_event": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "blocked_pangle_app_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "brand_safety_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "budget": {
                        "type": "float"
                    },
                    "budget_mode": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "catalog_authorized_bc_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "catalog_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "category_id": {
                        "type": "long"
                    },
                    "click_attribution_window": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "comment_disabled": {
                        "type": "boolean"
                    },
                    "conversion_bid_price": {
                        "type": "float"
                    },
                    "create_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "creative_material_mode": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "dayparting": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_bid_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_cpa_bid": {
                        "type": "float"
                    },
                    "deep_funnel_event_source": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_funnel_event_source_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_funnel_optimization_event": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_funnel_optimization_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "excluded_audience_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "gender": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "interest_category_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "inventory_filter_enabled": {
                        "type": "boolean"
                    },
                    "ios14_quota_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "is_hfss": {
                        "type": "boolean"
                    },
                    "is_new_structure": {
                        "type": "boolean"
                    },
                    "is_smart_performance_campaign": {
                        "type": "boolean"
                    },
                    "languages": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "location_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "modify_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "operation_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "optimization_event": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "optimization_goal": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "pacing": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "pixel_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "placement_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "placements": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "product_source": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "promotion_target_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "promotion_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "promotion_website_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "purchase_intention_keyword_ids": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "roas_bid": {
                        "type": "float"
                    },
                    "saved_audience_id": {
                        "type": "long"
                    },
                    "schedule_end_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "schedule_start_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "schedule_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "scheduled_budget": {
                        "type": "float"
                    },
                    "search_result_enabled": {
                        "type": "boolean"
                    },
                    "secondary_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "share_disabled": {
                        "type": "boolean"
                    },
                    "shopping_ads_retargeting_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "shopping_ads_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "skip_learning_phase": {
                        "type": "boolean"
                    },
                    "smart_audience_enabled": {
                        "type": "boolean"
                    },
                    "smart_interest_behavior_enabled": {
                        "type": "boolean"
                    },
                    "spending_power": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "split_test_group_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "split_test_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "store_authorized_bc_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "store_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "targeting_expansion": {
                        "properties": {
                        "expansion_enabled": {
                            "type": "boolean"
                        }
                        }
                    },
                    "tiktok_subplacements": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "vertical_sensitivity_id": {
                        "type": "long"
                    },
                    "video_download_disabled": {
                        "type": "boolean"
                    },
                    "view_attribution_window": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    }
                    }
                },
                "advertiser": {
                    "properties": {
                    "address": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "advertiser_account_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "advertiser_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "balance": {
                        "type": "float"
                    },
                    "cellphone_number": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "company": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "contacter": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "country": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "create_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "currency": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "description": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "display_timezone": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "email": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "industry": {
                        "type": "long"
                    },
                    "language": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "license_no": {
                        "type": "long"
                    },
                    "license_url": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "owner_bc_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "promotion_area": {
                        "type": "long"
                    },
                    "rejection_reason": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "role": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "telephone_number": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "timezone": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    }
                    }
                },
                "app_install": {
                    "type": "long"
                },
                "average_video_play": {
                    "type": "double"
                },
                "average_video_play_per_user": {
                    "type": "double"
                },
                "billed_cost": {
                    "type": "long"
                },
                "campaign": {
                    "properties": {
                    "advertiser_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "app_promotion_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "bid_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "budget": {
                        "type": "float"
                    },
                    "budget_mode": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "budget_optimize_on": {
                        "type": "boolean"
                    },
                    "campaign_app_profile_page_state": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_name": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_product_source": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "campaign_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "catalog_enabled": {
                        "type": "boolean"
                    },
                    "create_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "is_advanced_dedicated_campaign": {
                        "type": "boolean"
                    },
                    "is_new_structure": {
                        "type": "boolean"
                    },
                    "is_search_campaign": {
                        "type": "boolean"
                    },
                    "is_smart_performance_campaign": {
                        "type": "boolean"
                    },
                    "modify_time": {
                        "type": "date",
                        "format": "strict_date_optional_time"
                    },
                    "objective": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "objective_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "operation_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "optimization_goal": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": true,
                            "ignore_above": 256
                        }
                        }
                    },
                    "rf_campaign_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "roas_bid": {
                        "type": "float"
                    },
                    "rta_bid_enabled": {
                        "type": "boolean"
                    },
                    "rta_product_selection_enabled": {
                        "type": "boolean"
                    },
                    "sales_destination": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "secondary_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "virtual_objective_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    }
                    }
                },
                "cash_spend": {
                    "type": "long"
                },
                "clicks": {
                    "type": "long"
                },
                "conversion": {
                    "type": "long"
                },
                "conversion_rate": {
                    "type": "double"
                },
                "conversion_rate_v2": {
                    "type": "double"
                },
                "cost_per_1000_reached": {
                    "type": "long"
                },
                "cost_per_app_install": {
                    "type": "long"
                },
                "cost_per_conversion": {
                    "type": "long"
                },
                "cost_per_cta_conversion": {
                    "type": "long"
                },
                "cost_per_cta_purchase": {
                    "type": "long"
                },
                "cost_per_engaged_view_through_conversion": {
                    "type": "long"
                },
                "cost_per_evta_payments_completed": {
                    "type": "long"
                },
                "cost_per_evta_purchase": {
                    "type": "long"
                },
                "cost_per_purchase": {
                    "type": "long"
                },
                "cost_per_registration": {
                    "type": "long"
                },
                "cost_per_result": {
                    "type": "long"
                },
                "cost_per_secondary_goal_result": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "eager_global_ordinals": true,
                        "ignore_above": 256
                    }
                    }
                },
                "cost_per_total_purchase": {
                    "type": "long"
                },
                "cost_per_total_registration": {
                    "type": "long"
                },
                "cost_per_vta_conversion": {
                    "type": "long"
                },
                "cost_per_vta_payments_completed": {
                    "type": "long"
                },
                "cost_per_vta_purchase": {
                    "type": "long"
                },
                "cpc": {
                    "type": "long"
                },
                "cpm": {
                    "type": "long"
                },
                "cta_conversion": {
                    "type": "long"
                },
                "cta_purchase": {
                    "type": "long"
                },
                "ctr": {
                    "type": "double"
                },
                "engaged_view": {
                    "type": "long"
                },
                "engaged_view_15s": {
                    "type": "long"
                },
                "engaged_view_through_conversions": {
                    "type": "long"
                },
                "evta_payments_completed": {
                    "type": "long"
                },
                "evta_purchase": {
                    "type": "long"
                },
                "frequency": {
                    "type": "double"
                },
                "gross_impressions": {
                    "type": "long"
                },
                "impressions": {
                    "type": "long"
                },
                "live_effective_views": {
                    "type": "long"
                },
                "live_product_clicks": {
                    "type": "long"
                },
                "live_unique_views": {
                    "type": "long"
                },
                "live_views": {
                    "type": "long"
                },
                "paid_engaged_view": {
                    "type": "long"
                },
                "paid_engaged_view_15s": {
                    "type": "long"
                },
                "paid_engagement_engaged_view": {
                    "type": "long"
                },
                "paid_engagement_engaged_view_15s": {
                    "type": "long"
                },
                "purchase": {
                    "type": "long"
                },
                "purchase_rate": {
                    "type": "double"
                },
                "reach": {
                    "type": "long"
                },
                "real_time_app_install": {
                    "type": "long"
                },
                "real_time_app_install_cost": {
                    "type": "long"
                },
                "real_time_conversion": {
                    "type": "long"
                },
                "real_time_conversion_rate": {
                    "type": "double"
                },
                "real_time_conversion_rate_v2": {
                    "type": "double"
                },
                "real_time_cost_per_conversion": {
                    "type": "long"
                },
                "real_time_cost_per_result": {
                    "type": "long"
                },
                "real_time_result": {
                    "type": "long"
                },
                "real_time_result_rate": {
                    "type": "double"
                },
                "registration": {
                    "type": "long"
                },
                "registration_rate": {
                    "type": "double"
                },
                "result": {
                    "type": "long"
                },
                "result_rate": {
                    "type": "double"
                },
                "secondary_goal_result": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "eager_global_ordinals": true,
                        "ignore_above": 256
                    }
                    }
                },
                "secondary_goal_result_rate": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "eager_global_ordinals": true,
                        "ignore_above": 256
                    }
                    }
                },
                "spend": {
                    "type": "long"
                },
                "stat_time_day": {
                    "type": "date"
                },
                "total_active_pay_roas": {
                    "type": "double"
                },
                "total_purchase": {
                    "type": "long"
                },
                "total_purchase_value": {
                    "type": "long"
                },
                "total_registration": {
                    "type": "long"
                },
                "value_per_total_purchase": {
                    "type": "long"
                },
                "video_play_actions": {
                    "type": "long"
                },
                "video_watched_2s": {
                    "type": "long"
                },
                "video_watched_6s": {
                    "type": "long"
                },
                "voucher_spend": {
                    "type": "long"
                },
                "vta_complete_payment": {
                    "type": "long"
                },
                "vta_complete_payment_roas": {
                    "type": "double"
                },
                "vta_complete_payment_value": {
                    "type": "long"
                },
                "vta_conversion": {
                    "type": "long"
                },
                "vta_purchase": {
                    "type": "long"
                }
                }
            }
        }
        '''),
        id_field="customer_id",
        agg_field="customer_id",
        time_field="date",
    )
    return response


async def create_crm_fb_mappings(
    index_name: str, vada_uid: str, account_email: str
) -> Dict:
    """Copy CRM mappings from the mappings service
    Args:
        index_name: Name of the index to copy mappings for
        vada_uid: Vada user ID
        account_email: Account email of the Google account - for friendly name
    """

    async def create_crm_mappings_handler(
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mappings: Dict,
        id_field: str = "",
        agg_field: str = "",
        time_field: str = "",
    ) -> Dict:
        url = f"{settings.MAPPINGS_BASE_URL}/crm/mappings"

        payload = {
            "user_id": user_id,
            "index_name": index_name,
            "index_friendly_name": index_friendly_name,
            "mappings": mappings,
            "id_field": id_field,
            "agg_field": agg_field,
            "time_field": time_field,
        }
        return await put(url, json=payload)

    response = await create_crm_mappings_handler(
        user_id=vada_uid,
        index_name=index_name,
        index_friendly_name=f"Facebook Ads {account_email}",
        mappings=json.loads('''
        {
            "mappings": {
                "_doc": {
                "properties": {
                    "_vada": {
                    "properties": {
                        "ingest": {
                        "properties": {
                            "destination": {
                            "properties": {
                                "index": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "type": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "doc_id": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            },
                            "source": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            },
                            "type": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            },
                            "vada_client_id": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            }
                        }
                        }
                    }
                    },
                    "account_id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "account_status": {
                    "type": "long"
                    },
                    "ad_account": {
                    "properties": {
                        "account_id": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "account_status": {
                        "type": "long"
                        },
                        "age": {
                        "type": "float"
                        },
                        "all_capabilities": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "amount_spent": {
                        "type": "long"
                        },
                        "balance": {
                        "type": "long"
                        },
                        "business_city": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "business_country_code": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "business_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "business_state": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "business_street": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "business_street2": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "business_zip": {
                        "type": "long"
                        },
                        "currency": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "disable_reason": {
                        "type": "long"
                        },
                        "end_advertiser": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "end_advertiser_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "fb_entity": {
                        "type": "long"
                        },
                        "id": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "ad_active_time": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "ad_review_feedback": {
                    "properties": {
                        "global": {
                        "properties": {
                            "Phương thức kinh doanh không chấp nhận được": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            }
                        }
                        }
                    }
                    },
                    "adset": {
                    "properties": {
                        "id": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "adset_id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "age": {
                    "type": "float"
                    },
                    "amount_spent": {
                    "type": "float"
                    },
                    "balance": {
                    "type": "float"
                    },
                    "bid_amount": {
                    "type": "long"
                    },
                    "bid_info": {
                    "properties": {
                        "ACTIONS": {
                        "type": "long"
                        }
                    }
                    },
                    "bid_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "business_city": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "business_country_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "business_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "business_state": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "business_street": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "business_street2": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "business_zip": {
                    "type": "long"
                    },
                    "campaign": {
                    "properties": {
                        "id": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "campaign_id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "client_id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "configured_status": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "conversion_specs": {
                    "properties": {
                        "action": {
                        "properties": {
                            "leadgen": {
                            "properties": {
                                "leadgen": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "link_click": {
                            "properties": {
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "offsite_conversion": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "offsite_engagement": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "onsite_conversion": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "post_engagement": {
                            "properties": {
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "video_view": {
                            "properties": {
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                    },
                    "created_time": {
                    "type": "date"
                    },
                    "creative": {
                    "properties": {
                        "id": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "currency": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "demolink_hash": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "disable_reason": {
                    "type": "long"
                    },
                    "display_sequence": {
                    "type": "long"
                    },
                    "effective_status": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "end_advertiser": {
                    "type": "long"
                    },
                    "end_advertiser_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "end_time": {
                    "type": "long"
                    },
                    "engagement_audience": {
                    "type": "boolean"
                    },
                    "failed_delivery_checks": {
                    "properties": {
                        "check_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "description": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "extra_info": {
                        "properties": {
                            "countries": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            }
                        }
                        },
                        "summary": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "fb_entity": {
                    "type": "long"
                    },
                    "id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "insight": {
                    "properties": {
                        "account_currency": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "action_values": {
                        "properties": {
                            "add_to_cart": {
                            "type": "long"
                            },
                            "lead": {
                            "type": "long"
                            },
                            "offsite_conversion": {
                            "properties": {
                                "custom": {
                                "properties": {
                                    "467117139737973": {
                                    "type": "long"
                                    }
                                }
                                },
                                "fb_pixel_add_to_cart": {
                                "type": "long"
                                },
                                "fb_pixel_purchase": {
                                "type": "long"
                                }
                            }
                            },
                            "omni_add_to_cart": {
                            "type": "long"
                            },
                            "omni_initiated_checkout": {
                            "type": "long"
                            },
                            "omni_purchase": {
                            "type": "long"
                            },
                            "onsite_app_purchase": {
                            "type": "long"
                            },
                            "onsite_conversion": {
                            "properties": {
                                "initiate_checkout": {
                                "type": "long"
                                },
                                "lead": {
                                "type": "long"
                                },
                                "lead_grouped": {
                                "type": "long"
                                },
                                "purchase": {
                                "type": "long"
                                }
                            }
                            },
                            "onsite_web_add_to_cart": {
                            "type": "long"
                            },
                            "onsite_web_app_add_to_cart": {
                            "type": "long"
                            },
                            "onsite_web_app_purchase": {
                            "type": "long"
                            },
                            "onsite_web_initiate_checkout": {
                            "type": "long"
                            },
                            "onsite_web_lead": {
                            "type": "long"
                            },
                            "onsite_web_purchase": {
                            "type": "long"
                            },
                            "purchase": {
                            "type": "long"
                            },
                            "web_app_in_store_purchase": {
                            "type": "long"
                            },
                            "web_in_store_purchase": {
                            "type": "long"
                            }
                        }
                        },
                        "actions": {
                        "properties": {
                            "add_to_cart": {
                            "type": "long"
                            },
                            "comment": {
                            "type": "long"
                            },
                            "landing_page_view": {
                            "type": "long"
                            },
                            "lead": {
                            "type": "long"
                            },
                            "like": {
                            "type": "long"
                            },
                            "link_click": {
                            "type": "long"
                            },
                            "offsite_conversion": {
                            "properties": {
                                "custom": {
                                "properties": {
                                    "467117139737973": {
                                    "type": "long"
                                    }
                                }
                                },
                                "fb_pixel_add_to_cart": {
                                "type": "long"
                                },
                                "fb_pixel_custom": {
                                "type": "long"
                                },
                                "fb_pixel_purchase": {
                                "type": "long"
                                },
                                "fb_pixel_view_content": {
                                "type": "long"
                                }
                            }
                            },
                            "omni_add_to_cart": {
                            "type": "long"
                            },
                            "omni_initiated_checkout": {
                            "type": "long"
                            },
                            "omni_landing_page_view": {
                            "type": "long"
                            },
                            "omni_purchase": {
                            "type": "long"
                            },
                            "omni_view_content": {
                            "type": "long"
                            },
                            "onsite_app_purchase": {
                            "type": "long"
                            },
                            "onsite_conversion": {
                            "properties": {
                                "initiate_checkout": {
                                "type": "long"
                                },
                                "lead": {
                                "type": "long"
                                },
                                "lead_grouped": {
                                "type": "long"
                                },
                                "messaging_block": {
                                "type": "long"
                                },
                                "messaging_business_calling_opt_in_accepted": {
                                "type": "long"
                                },
                                "messaging_business_calling_opt_in_sent": {
                                "type": "long"
                                },
                                "messaging_conversation_replied_7d": {
                                "type": "long"
                                },
                                "messaging_conversation_started_7d": {
                                "type": "long"
                                },
                                "messaging_first_reply": {
                                "type": "long"
                                },
                                "messaging_order_created_v2": {
                                "type": "long"
                                },
                                "messaging_order_shipped_v2": {
                                "type": "long"
                                },
                                "messaging_user_call_placed": {
                                "type": "long"
                                },
                                "messaging_user_depth_2_message_send": {
                                "type": "long"
                                },
                                "messaging_user_depth_3_message_send": {
                                "type": "long"
                                },
                                "messaging_user_depth_5_message_send": {
                                "type": "long"
                                },
                                "messaging_user_subscribed": {
                                "type": "long"
                                },
                                "messaging_welcome_message_view": {
                                "type": "long"
                                },
                                "post_save": {
                                "type": "long"
                                },
                                "purchase": {
                                "type": "long"
                                },
                                "total_messaging_connection": {
                                "type": "long"
                                }
                            }
                            },
                            "onsite_web_add_to_cart": {
                            "type": "long"
                            },
                            "onsite_web_app_add_to_cart": {
                            "type": "long"
                            },
                            "onsite_web_app_purchase": {
                            "type": "long"
                            },
                            "onsite_web_app_view_content": {
                            "type": "long"
                            },
                            "onsite_web_initiate_checkout": {
                            "type": "long"
                            },
                            "onsite_web_lead": {
                            "type": "long"
                            },
                            "onsite_web_purchase": {
                            "type": "long"
                            },
                            "onsite_web_view_content": {
                            "type": "long"
                            },
                            "page_engagement": {
                            "type": "long"
                            },
                            "photo_view": {
                            "type": "long"
                            },
                            "post": {
                            "type": "long"
                            },
                            "post_engagement": {
                            "type": "long"
                            },
                            "post_reaction": {
                            "type": "long"
                            },
                            "purchase": {
                            "type": "long"
                            },
                            "video_view": {
                            "type": "long"
                            },
                            "view_content": {
                            "type": "long"
                            },
                            "web_app_in_store_purchase": {
                            "type": "long"
                            },
                            "web_in_store_purchase": {
                            "type": "long"
                            }
                        }
                        },
                        "adset_id": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "buying_type": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "canvas_avg_view_percent": {
                        "type": "long"
                        },
                        "canvas_avg_view_time": {
                        "type": "long"
                        },
                        "clicks": {
                        "type": "long"
                        },
                        "conversion_rate_ranking": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "conversions": {
                        "properties": {
                            "offsite_conversion": {
                            "properties": {
                                "fb_pixel_custom": {
                                "properties": {
                                    "ClickButton": {
                                    "type": "long"
                                    }
                                }
                                }
                            }
                            }
                        }
                        },
                        "cost_per_15_sec_video_view": {
                        "properties": {
                            "video_view": {
                            "type": "float"
                            }
                        }
                        },
                        "cost_per_2_sec_continuous_video_view": {
                        "properties": {
                            "video_view": {
                            "type": "float"
                            }
                        }
                        },
                        "cost_per_action_type": {
                        "properties": {
                            "add_to_cart": {
                            "type": "long"
                            },
                            "landing_page_view": {
                            "type": "long"
                            },
                            "lead": {
                            "type": "long"
                            },
                            "like": {
                            "type": "long"
                            },
                            "link_click": {
                            "type": "float"
                            },
                            "offsite_conversion": {
                            "properties": {
                                "custom": {
                                "properties": {
                                    "467117139737973": {
                                    "type": "long"
                                    }
                                }
                                },
                                "fb_pixel_custom": {
                                "type": "long"
                                }
                            }
                            },
                            "omni_add_to_cart": {
                            "type": "long"
                            },
                            "omni_initiated_checkout": {
                            "type": "long"
                            },
                            "omni_landing_page_view": {
                            "type": "long"
                            },
                            "omni_purchase": {
                            "type": "long"
                            },
                            "omni_view_content": {
                            "type": "long"
                            },
                            "onsite_app_purchase": {
                            "type": "long"
                            },
                            "onsite_conversion": {
                            "properties": {
                                "initiate_checkout": {
                                "type": "long"
                                },
                                "lead": {
                                "type": "long"
                                },
                                "lead_grouped": {
                                "type": "long"
                                },
                                "messaging_block": {
                                "type": "long"
                                },
                                "messaging_business_calling_opt_in_accepted": {
                                "type": "long"
                                },
                                "messaging_business_calling_opt_in_sent": {
                                "type": "long"
                                },
                                "messaging_conversation_replied_7d": {
                                "type": "float"
                                },
                                "messaging_conversation_started_7d": {
                                "type": "float"
                                },
                                "messaging_first_reply": {
                                "type": "float"
                                },
                                "messaging_order_created_v2": {
                                "type": "long"
                                },
                                "messaging_order_shipped_v2": {
                                "type": "long"
                                },
                                "messaging_user_call_placed": {
                                "type": "long"
                                },
                                "messaging_user_depth_2_message_send": {
                                "type": "float"
                                },
                                "messaging_user_depth_3_message_send": {
                                "type": "float"
                                },
                                "messaging_user_depth_5_message_send": {
                                "type": "long"
                                },
                                "messaging_user_subscribed": {
                                "type": "float"
                                },
                                "messaging_welcome_message_view": {
                                "type": "float"
                                },
                                "post_save": {
                                "type": "long"
                                },
                                "total_messaging_connection": {
                                "type": "float"
                                }
                            }
                            },
                            "onsite_web_add_to_cart": {
                            "type": "long"
                            },
                            "onsite_web_app_add_to_cart": {
                            "type": "long"
                            },
                            "onsite_web_app_purchase": {
                            "type": "long"
                            },
                            "onsite_web_app_view_content": {
                            "type": "long"
                            },
                            "onsite_web_initiate_checkout": {
                            "type": "long"
                            },
                            "onsite_web_lead": {
                            "type": "long"
                            },
                            "onsite_web_purchase": {
                            "type": "long"
                            },
                            "onsite_web_view_content": {
                            "type": "long"
                            },
                            "page_engagement": {
                            "type": "float"
                            },
                            "post_engagement": {
                            "type": "float"
                            },
                            "purchase": {
                            "type": "long"
                            },
                            "video_view": {
                            "type": "float"
                            },
                            "view_content": {
                            "type": "long"
                            },
                            "web_in_store_purchase": {
                            "type": "long"
                            }
                        }
                        },
                        "cost_per_conversion": {
                        "properties": {
                            "offsite_conversion": {
                            "properties": {
                                "fb_pixel_custom": {
                                "properties": {
                                    "ClickButton": {
                                    "type": "long"
                                    }
                                }
                                }
                            }
                            }
                        }
                        },
                        "cost_per_estimated_ad_recallers": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "cost_per_inline_link_click": {
                        "type": "float"
                        },
                        "cost_per_inline_post_engagement": {
                        "type": "float"
                        },
                        "cost_per_outbound_click": {
                        "properties": {
                            "outbound_click": {
                            "type": "long"
                            }
                        }
                        },
                        "cost_per_thruplay": {
                        "properties": {
                            "video_view": {
                            "type": "float"
                            }
                        }
                        },
                        "cost_per_unique_action_type": {
                        "properties": {
                            "link_click": {
                            "type": "float"
                            },
                            "onsite_conversion": {
                            "properties": {
                                "messaging_business_calling_opt_in_accepted": {
                                "type": "long"
                                },
                                "messaging_first_reply": {
                                "type": "long"
                                },
                                "messaging_user_depth_5_message_send": {
                                "type": "long"
                                },
                                "returning_messaging_connection": {
                                "type": "long"
                                },
                                "total_messaging_connection": {
                                "type": "long"
                                }
                            }
                            },
                            "onsite_web_initiate_checkout": {
                            "type": "long"
                            }
                        }
                        },
                        "cost_per_unique_click": {
                        "type": "float"
                        },
                        "cost_per_unique_inline_link_click": {
                        "type": "float"
                        },
                        "cost_per_unique_outbound_click": {
                        "properties": {
                            "outbound_click": {
                            "type": "long"
                            }
                        }
                        },
                        "cpc": {
                        "type": "float"
                        },
                        "cpm": {
                        "type": "float"
                        },
                        "cpp": {
                        "type": "float"
                        },
                        "created_time": {
                        "type": "date"
                        },
                        "ctr": {
                        "type": "float"
                        },
                        "date_start": {
                        "type": "date"
                        },
                        "date_stop": {
                        "type": "date"
                        },
                        "engagement_rate_ranking": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "frequency": {
                        "type": "long"
                        },
                        "full_view_impressions": {
                        "type": "long"
                        },
                        "full_view_reach": {
                        "type": "long"
                        },
                        "impressions": {
                        "type": "long"
                        },
                        "inline_link_click_ctr": {
                        "type": "float"
                        },
                        "inline_link_clicks": {
                        "type": "long"
                        },
                        "inline_post_engagement": {
                        "type": "long"
                        },
                        "instagram_upcoming_event_reminders_set": {
                        "type": "long"
                        },
                        "instant_experience_clicks_to_open": {
                        "type": "long"
                        },
                        "instant_experience_clicks_to_start": {
                        "type": "long"
                        },
                        "objective": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "optimization_goal": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "outbound_clicks": {
                        "properties": {
                            "outbound_click": {
                            "type": "long"
                            }
                        }
                        },
                        "outbound_clicks_ctr": {
                        "properties": {
                            "outbound_click": {
                            "type": "float"
                            }
                        }
                        },
                        "reach": {
                        "type": "long"
                        },
                        "social_spend": {
                        "type": "long"
                        },
                        "spend": {
                        "type": "long"
                        },
                        "unique_actions": {
                        "properties": {
                            "link_click": {
                            "type": "long"
                            },
                            "onsite_conversion": {
                            "properties": {
                                "messaging_first_reply": {
                                "type": "long"
                                },
                                "messaging_user_depth_5_message_send": {
                                "type": "long"
                                },
                                "returning_messaging_connection": {
                                "type": "long"
                                },
                                "total_messaging_connection": {
                                "type": "long"
                                }
                            }
                            },
                            "onsite_web_initiate_checkout": {
                            "type": "long"
                            }
                        }
                        },
                        "unique_clicks": {
                        "type": "long"
                        },
                        "unique_ctr": {
                        "type": "float"
                        },
                        "unique_inline_link_click_ctr": {
                        "type": "float"
                        },
                        "unique_inline_link_clicks": {
                        "type": "long"
                        },
                        "unique_link_clicks_ctr": {
                        "type": "float"
                        },
                        "unique_outbound_clicks": {
                        "properties": {
                            "outbound_click": {
                            "type": "long"
                            }
                        }
                        },
                        "unique_outbound_clicks_ctr": {
                        "properties": {
                            "outbound_click": {
                            "type": "float"
                            }
                        }
                        },
                        "unique_video_continuous_2_sec_watched_actions": {
                        "properties": {
                            "video_view": {
                            "type": "long"
                            }
                        }
                        },
                        "unique_video_view_15_sec": {
                        "properties": {
                            "video_view": {
                            "type": "long"
                            }
                        }
                        },
                        "updated_time": {
                        "type": "date"
                        },
                        "video_15_sec_watched_actions": {
                        "properties": {
                            "video_view": {
                            "type": "long"
                            }
                        }
                        },
                        "video_30_sec_watched_actions": {
                        "properties": {
                            "video_view": {
                            "type": "long"
                            }
                        }
                        },
                        "video_avg_time_watched_actions": {
                        "properties": {
                            "video_view": {
                            "type": "long"
                            }
                        }
                        },
                        "video_continuous_2_sec_watched_actions": {
                        "properties": {
                            "video_view": {
                            "type": "long"
                            }
                        }
                        },
                        "video_play_actions": {
                        "properties": {
                            "video_view": {
                            "type": "long"
                            }
                        }
                        },
                        "website_ctr": {
                        "properties": {
                            "link_click": {
                            "type": "float"
                            }
                        }
                        },
                        "website_purchase_roas": {
                        "properties": {
                            "offsite_conversion": {
                            "properties": {
                                "fb_pixel_purchase": {
                                "type": "float"
                                }
                            }
                            }
                        }
                        }
                    }
                    },
                    "issues_info": {
                    "properties": {
                        "error_code": {
                        "type": "long"
                        },
                        "error_message": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "error_summary": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "error_type": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "level": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "mid": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "opes_mid": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "last_updated_by_app_id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "preview_shareable_link": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "recommendations": {
                    "properties": {
                        "blame_field": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "code": {
                        "type": "long"
                        },
                        "confidence": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "importance": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "message": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "title": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "source_ad": {
                    "properties": {
                        "id": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        }
                    }
                    },
                    "source_ad_id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "start_time": {
                    "type": "date"
                    },
                    "status": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                        }
                    }
                    },
                    "targeting": {
                    "properties": {
                        "age_max": {
                        "type": "long"
                        },
                        "age_min": {
                        "type": "long"
                        },
                        "age_range": {
                        "type": "long"
                        },
                        "audience_network_positions": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "brand_safety_content_filter_levels": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "custom_audiences": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "device_platforms": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "excluded_custom_audiences": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "excluded_geo_locations": {
                        "properties": {
                            "custom_locations": {
                            "properties": {
                                "country": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "custom_type": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "max_population": {
                                "type": "long"
                                },
                                "min_population": {
                                "type": "long"
                                }
                            }
                            },
                            "location_types": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            }
                        }
                        },
                        "facebook_positions": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "flexible_spec": {
                        "properties": {
                            "behaviors": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            },
                            "interests": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            }
                        }
                        },
                        "genders": {
                        "type": "long"
                        },
                        "geo_locations": {
                        "properties": {
                            "cities": {
                            "properties": {
                                "country": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "distance_unit": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "key": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "name": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "radius": {
                                "type": "long"
                                },
                                "region": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "region_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "countries": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            },
                            "custom_locations": {
                            "properties": {
                                "country": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "custom_type": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "max_population": {
                                "type": "long"
                                },
                                "min_population": {
                                "type": "long"
                                }
                            }
                            },
                            "location_types": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                                }
                            }
                            },
                            "regions": {
                            "properties": {
                                "country": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "key": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "name": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            }
                        }
                        },
                        "instagram_positions": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "locales": {
                        "type": "long"
                        },
                        "messenger_positions": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "publisher_platforms": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "targeting_automation": {
                        "properties": {
                            "advantage_audience": {
                            "type": "long"
                            },
                            "individual_setting": {
                            "properties": {
                                "age": {
                                "type": "long"
                                },
                                "gender": {
                                "type": "long"
                                }
                            }
                            }
                        }
                        },
                        "targeting_optimization": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "targeting_relaxation_types": {
                        "properties": {
                            "custom_audience": {
                            "type": "long"
                            },
                            "lookalike": {
                            "type": "long"
                            }
                        }
                        }
                    }
                    },
                    "tracking_and_conversion_with_defaults": {
                    "properties": {
                        "custom_tracking": {
                        "properties": {
                            "action": {
                            "properties": {
                                "offline_conversion": {
                                "properties": {
                                    "dataset": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "offsite_conversion": {
                                "properties": {
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                }
                            }
                            }
                        }
                        },
                        "default_conversion": {
                        "properties": {
                            "action": {
                            "properties": {
                                "leadgen": {
                                "type": "object"
                                },
                                "link_click": {
                                "properties": {
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "offsite_conversion": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "offsite_engagement": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "onsite_conversion": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "post_engagement": {
                                "properties": {
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "video_view": {
                                "properties": {
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                }
                            }
                            }
                        }
                        },
                        "default_tracking": {
                        "properties": {
                            "action": {
                            "properties": {
                                "attention_event": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "canvas_view_time": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "card_view": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "commerce_event": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "dwell": {
                                "properties": {
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "faqs_sticker_icebreaker_click": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "landing_page_view": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "link_click": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "messenger": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "offsite_conversion": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "onsite_conversion": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "post_engagement": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "resurfaced_ad_clicks": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "resurfaced_ad_impression": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "creative": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "fb_pixel": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                },
                                "whatsapp": {
                                "properties": {
                                    "conversion_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "page": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    },
                                    "post_wall": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                        }
                                    }
                                    }
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                    },
                    "tracking_specs": {
                    "properties": {
                        "action": {
                        "properties": {
                            "attention_event": {
                            "properties": {
                                "creative": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "commerce_event": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "link_click": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "creative": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "dataset": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "fb_pixel": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "messenger": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "creative": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "dataset": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "fb_pixel": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "offline_conversion": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "dataset": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "fb_pixel": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "offsite_conversion": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "dataset": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "fb_pixel": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "onsite_conversion": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "creative": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "dataset": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "fb_pixel": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "post_engagement": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "creative": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "dataset": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "fb_pixel": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            },
                            "whatsapp": {
                            "properties": {
                                "conversion_id": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "page": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                },
                                "post_wall": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                    }
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                    },
                    "updated_time": {
                    "type": "date"
                    }
                }
                }
            }
        }
        '''),
        id_field="customer_id",
        agg_field="customer_id",
        time_field="date",
    )
    return response