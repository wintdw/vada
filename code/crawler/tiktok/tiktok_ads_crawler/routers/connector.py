from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from tools import get_logger
from tools.settings import settings

from repositories import upsert_crawl_info
from models import CrawlInfo

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/ingest/partner/tiktok/ad/callback", tags=["Connector"])
async def ingest_partner_tiktok_ad_callback(auth_code: str, state: str):

    from services import (
        tiktok_biz_get_access_token,
        tiktok_biz_get_user_info,
        create_crm_mappings
    )

    try:
        access_token = await tiktok_biz_get_access_token(auth_code=auth_code)
        logger.info(access_token)
        user_info = await tiktok_biz_get_user_info(access_token=access_token.get("access_token"))
        logger.info(user_info)
        
        crawl_info = await upsert_crawl_info(CrawlInfo(
            account_id=user_info["core_user_id"],
            account_email=user_info["email"],
            vada_uid=state,
            access_token=access_token.get("access_token"),
            index_name=f"data_tiktokad_{state}",
            crawl_type="tiktok_business_ads"
        ))
        logger.info(crawl_info)

        mappings_response = await create_crm_mappings(
            index_name=crawl_info.index_name,
            vada_uid=state,
            account_email=user_info["email"],
        )
        logger.info(mappings_response)

        encoded_friendly_name = urlencode({"friendly_index_name": f"Tiktok Ads {user_info['email']}"})
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    return RedirectResponse(url=f"{settings.CONNECTOR_CALLBACK_URL}?account_id={user_info["core_user_id"]}&account_email={user_info["email"]}&index_name={crawl_info.index_name}&{encoded_friendly_name}")

@router.get("/ingest/partner/tiktok/ad/auth", tags=["Connector"])
async def ingest_partner_tiktok_ad_auth(vada_uid: str):
    return RedirectResponse(url=f"https://business-api.tiktok.com/portal/auth?app_id=7480814660439146497&state={vada_uid}&redirect_uri={settings.TIKTOK_BIZ_REDIRECT_URI}")

@router.get("/ingest/partner/tiktok/ad/config", tags=["Connector"])
async def ingest_partner_tiktok_ad_config():
    return {
        "mappings": {
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
                            "ignore_above": 256
                        }
                        }
                    },
                    "video_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": True,
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
                        "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_funnel_event_source_id": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": True,
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_funnel_optimization_event": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": True,
                            "ignore_above": 256
                        }
                        }
                    },
                    "deep_funnel_optimization_status": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
                            "ignore_above": 256
                        }
                        }
                    },
                    "promotion_target_type": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                            "eager_global_ordinals": True,
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
                        "eager_global_ordinals": True,
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
                        "eager_global_ordinals": True,
                        "ignore_above": 256
                    }
                    }
                },
                "secondary_goal_result_rate": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "eager_global_ordinals": True,
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