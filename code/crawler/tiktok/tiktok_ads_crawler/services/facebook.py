from facebook_business import FacebookAdsApi
from facebook_business.adobjects.adaccountuser import AdAccountUser
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights


import logging
from tools.settings import settings
from tools import get_logger

logger = get_logger(__name__, logging.INFO)


async def fetch_ad_accounts(access_token: str) -> list[AdAccount]:
    """
    Fetch ad accounts from Facebook API using the provided access token.

    Args:
        access_token (str): Facebook API access token.

    Returns:
        list[AdAccount]: List of ad accounts.
    """
    ads_api = FacebookAdsApi.init(
        app_id=settings.FACEBOOK_APP_ID,
        app_secret=settings.FACEBOOK_APP_SECRET,
        access_token=access_token,
    )
    aau = AdAccountUser("me", api=ads_api)
    ad_accounts = aau.get_ad_accounts(
        fields=[
            AdAccount.Field.account_id,
            AdAccount.Field.account_status,
            AdAccount.Field.age,
            AdAccount.Field.amount_spent,
            AdAccount.Field.balance,
            AdAccount.Field.disable_reason,
            AdAccount.Field.end_advertiser,
            AdAccount.Field.end_advertiser_name,
            AdAccount.Field.fb_entity,

            AdAccount.Field.name,
            # AdAccount.Field.all_capabilities,
            AdAccount.Field.currency,
            AdAccount.Field.business_city,
            AdAccount.Field.business_country_code,
            AdAccount.Field.business_name,
            AdAccount.Field.business_state,
            AdAccount.Field.business_street,
            AdAccount.Field.business_street2,
            AdAccount.Field.business_zip,
        ]
    )
    logger.info(f"Fetched {len(ad_accounts)} ad accounts.")
    return ad_accounts


async def fetch_ads_for_accounts(ad_accounts: list[AdAccount]):
    """
    Fetch ads for a list of ad accounts using batch requests.

    Args:
        ad_accounts (list[AdAccount]): List of ad accounts.
    """
    for ad_account in ad_accounts:
        ads = ad_account.get_ads(
            params={"limit": 100},
            fields=[
                Ad.Field.account_id,
                Ad.Field.ad_active_time,
                Ad.Field.ad_review_feedback,
                Ad.Field.ad_schedule_end_time,
                Ad.Field.ad_schedule_start_time,
                Ad.Field.adlabels,
                Ad.Field.adset,
                Ad.Field.adset_id,
                Ad.Field.bid_amount,
                Ad.Field.bid_info,
                Ad.Field.bid_type,
                Ad.Field.campaign_id,
                Ad.Field.configured_status,
                Ad.Field.conversion_domain,
                Ad.Field.conversion_specs,
                Ad.Field.created_time,
                Ad.Field.creative,
                Ad.Field.creative_asset_groups_spec,
                Ad.Field.demolink_hash,
                Ad.Field.display_sequence,
                Ad.Field.effective_status,
                Ad.Field.engagement_audience,
                Ad.Field.failed_delivery_checks,
                Ad.Field.id,
                Ad.Field.issues_info,
                Ad.Field.last_updated_by_app_id,
                Ad.Field.name,
                # Ad.Field.placement,
                Ad.Field.preview_shareable_link,
                Ad.Field.priority,
                Ad.Field.recommendations,
                Ad.Field.source_ad,
                Ad.Field.source_ad_id,
                Ad.Field.status,
                Ad.Field.targeting,
                Ad.Field.tracking_and_conversion_with_defaults,
                Ad.Field.tracking_specs,
                Ad.Field.updated_time,
                Ad.Field.adset_spec,
                Ad.Field.audience_id,
                Ad.Field.date_format,
                Ad.Field.draft_adgroup_id,
                Ad.Field.execution_options,
                Ad.Field.include_demolink_hashes,
                Ad.Field.filename,
            ],
        )
        all_ads = list(ads)
        logger.info(f"All ads: {len(all_ads)}")
        for ad in all_ads:
            ad.get_insights(
                params={"date_preset": "today"},
                fields=[
                    AdsInsights.Field.account_currency,
                    AdsInsights.Field.action_values,
                    AdsInsights.Field.actions,
                    AdsInsights.Field.ad_impression_actions,
                    AdsInsights.Field.adset_id,
                    AdsInsights.Field.attribution_setting,
                    AdsInsights.Field.auction_bid,
                    AdsInsights.Field.auction_competitiveness,
                    AdsInsights.Field.auction_max_competitor_bid,
                    AdsInsights.Field.buying_type,
                    AdsInsights.Field.canvas_avg_view_percent,
                    AdsInsights.Field.canvas_avg_view_time,
                    AdsInsights.Field.catalog_segment_actions,
                    AdsInsights.Field.catalog_segment_value,
                    AdsInsights.Field.catalog_segment_value_mobile_purchase_roas,
                    AdsInsights.Field.catalog_segment_value_omni_purchase_roas,
                    AdsInsights.Field.catalog_segment_value_website_purchase_roas,
                    AdsInsights.Field.clicks,
                    AdsInsights.Field.conversion_rate_ranking,
                    AdsInsights.Field.conversion_values,
                    AdsInsights.Field.conversions,
                    AdsInsights.Field.converted_product_quantity,
                    AdsInsights.Field.converted_product_value,
                    AdsInsights.Field.cost_per_15_sec_video_view,
                    AdsInsights.Field.cost_per_2_sec_continuous_video_view,
                    AdsInsights.Field.cost_per_action_type,
                    AdsInsights.Field.cost_per_ad_click,
                    AdsInsights.Field.cost_per_conversion,
                    AdsInsights.Field.cost_per_dda_countby_convs,
                    AdsInsights.Field.cost_per_estimated_ad_recallers,
                    AdsInsights.Field.cost_per_inline_link_click,
                    AdsInsights.Field.cost_per_inline_post_engagement,
                    AdsInsights.Field.cost_per_one_thousand_ad_impression,
                    AdsInsights.Field.cost_per_outbound_click,
                    AdsInsights.Field.cost_per_thruplay,
                    AdsInsights.Field.cost_per_unique_action_type,
                    AdsInsights.Field.cost_per_unique_click,
                    AdsInsights.Field.cost_per_unique_conversion,
                    AdsInsights.Field.cost_per_unique_inline_link_click,
                    AdsInsights.Field.cost_per_unique_outbound_click,
                    AdsInsights.Field.cpc,
                    AdsInsights.Field.cpm,
                    AdsInsights.Field.cpp,
                    AdsInsights.Field.created_time,
                    AdsInsights.Field.ctr,
                    AdsInsights.Field.date_start,
                    AdsInsights.Field.date_stop,
                    # AdsInsights.Field.dda_countby_convs,
                    # AdsInsights.Field.dda_results,
                    AdsInsights.Field.engagement_rate_ranking,
                    # AdsInsights.Field.estimated_ad_recall_rate,
                    # AdsInsights.Field.estimated_ad_recallers,
                    AdsInsights.Field.frequency,
                    AdsInsights.Field.full_view_impressions,
                    AdsInsights.Field.full_view_reach,
                    AdsInsights.Field.impressions,
                    AdsInsights.Field.inline_link_click_ctr,
                    AdsInsights.Field.inline_link_clicks,
                    AdsInsights.Field.inline_post_engagement,
                    AdsInsights.Field.instagram_upcoming_event_reminders_set,
                    AdsInsights.Field.instant_experience_clicks_to_open,
                    AdsInsights.Field.instant_experience_clicks_to_start,
                    AdsInsights.Field.instant_experience_outbound_clicks,
                    # AdsInsights.Field.interactive_component_tap,
                    AdsInsights.Field.marketing_messages_cost_per_delivered,
                    AdsInsights.Field.marketing_messages_cost_per_link_btn_click,
                    AdsInsights.Field.marketing_messages_spend,
                    AdsInsights.Field.marketing_messages_website_purchase_values,
                    AdsInsights.Field.mobile_app_purchase_roas,
                    AdsInsights.Field.objective,
                    # AdsInsights.Field.onsite_conversion_messaging_detected_purchase_deduped,
                    AdsInsights.Field.optimization_goal,
                    AdsInsights.Field.outbound_clicks,
                    AdsInsights.Field.outbound_clicks_ctr,
                    # AdsInsights.Field.place_page_name,
                    # AdsInsights.Field.purchase_roas,
                    # AdsInsights.Field.qualifying_question_qualify_answer_rate,
                    # AdsInsights.Field.quality_ranking,
                    AdsInsights.Field.reach,
                    # AdsInsights.Field.shops_assisted_purchases,
                    AdsInsights.Field.social_spend,
                    AdsInsights.Field.spend,
                    AdsInsights.Field.unique_actions,
                    AdsInsights.Field.unique_clicks,
                    AdsInsights.Field.unique_conversions,
                    AdsInsights.Field.unique_ctr,
                    AdsInsights.Field.unique_inline_link_click_ctr,
                    AdsInsights.Field.unique_inline_link_clicks,
                    AdsInsights.Field.unique_link_clicks_ctr,
                    AdsInsights.Field.unique_outbound_clicks,
                    AdsInsights.Field.unique_outbound_clicks_ctr,
                    AdsInsights.Field.unique_video_continuous_2_sec_watched_actions,
                    AdsInsights.Field.unique_video_view_15_sec,
                    AdsInsights.Field.updated_time,
                    AdsInsights.Field.video_15_sec_watched_actions,
                    AdsInsights.Field.video_30_sec_watched_actions,
                    AdsInsights.Field.video_avg_time_watched_actions,
                    AdsInsights.Field.video_continuous_2_sec_watched_actions,

                    # AdsInsights.Field.video_p100_watched_actions,
                    # AdsInsights.Field.video_p25_watched_actions,
                    # AdsInsights.Field.video_p50_watched_actions,
                    # AdsInsights.Field.video_p75_watched_actions,
                    # AdsInsights.Field.video_p95_watched_actions,
                    AdsInsights.Field.video_play_actions,
                    # AdsInsights.Field.video_play_curve_actions,
                    AdsInsights.Field.video_play_retention_0_to_15s_actions,
                    AdsInsights.Field.video_play_retention_20_to_60s_actions,
                    # AdsInsights.Field.video_play_retention_graph_actions,
                    # AdsInsights.Field.video_thruplay_watched_actions,
                    AdsInsights.Field.video_time_watched_actions,
                    AdsInsights.Field.website_ctr,
                    AdsInsights.Field.website_purchase_roas,
                ],
            )


async def crawl_facebook_ads(access_token: str = settings.FACEBOOK_ACCESS_TOKEN):
    """
    Crawl Facebook ads data.

    Args:
        access_token (str): Facebook API access token.
    """
    try:
        ad_accounts = await fetch_ad_accounts(access_token)
        await fetch_ads_for_accounts(ad_accounts)
        logger.info("Facebook ads crawling completed successfully.")
    except Exception as e:
        logger.error(f"Error occurred during Facebook ads crawling: {e}")
        raise