from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from tools import get_logger
from tools.settings import settings

from repositories import upsert_crawl_info
from models import CrawlInfo

router = APIRouter()
logger = get_logger(__name__, 20)

@router.get("/ingest/partner/facebook/ad/auth", tags=["Connector"])
async def ingest_partner_facebook_ad_auth(vada_uid: str):
    return RedirectResponse(url=f"https://www.facebook.com/v19.0/dialog/oauth?client_id=822555046472581&redirect_uri={settings.META_REDIRECT_URI}&state={vada_uid}&scope=email,public_profile,ads_management,business_management&config_id=528311813246288")

@router.get("/ingest/partner/facebook/ad/callback", tags=["Connector"])
async def ingest_partner_facebook_ad_callback(state: str, code: str):
    from services import (
        send_to_crawler_service,
        fetch_user_info,
        exchange_code_for_access_token
    )

    try:
        access_token = await exchange_code_for_access_token(code=code)
        logger.info(access_token)

        user_info = await fetch_user_info(access_token=access_token)
        logger.info(user_info)

        crawl_info = await upsert_crawl_info(CrawlInfo(
            account_id=user_info["id"],
            account_name=user_info["name"],
            vada_uid=state,
            access_token=access_token,
            index_name=f"data_fbad_{user_info["id"]}",
            crawl_type="facebook_business_ads"
        ))
        logger.info(crawl_info)

        response = await send_to_crawler_service(
            client_id=crawl_info.index_name,
            data={
                f"{crawl_info.index_name}": {
                    "token": f"{crawl_info.access_token}",
                    "destinations": [
                        {
                            "fb_type": "fb_ad",
                            "type": "elasticsearch",
                            "index": f"{crawl_info.index_name}",
                        }
                    ]
                }
            }
        )
        logger.info(response)

        encoded_friendly_name = urlencode({"friendly_index_name": f"Facebook Ads - {crawl_info.account_name}"})

    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    return RedirectResponse(url=f"{settings.CONNECTOR_CALLBACK_URL}?account_id={crawl_info.account_id}&account_name={crawl_info.account_name}&index_name={crawl_info.index_name}&{encoded_friendly_name}")

@router.get("/ingest/partner/facebook/ad/config", tags=["Connector"])
async def ingest_partner_facebook_ad_config():
    return {
        "mappings": {
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
