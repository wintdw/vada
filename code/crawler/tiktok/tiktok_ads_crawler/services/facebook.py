from tools.settings import settings
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.adaccountuser import AdAccountUser
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad


async def facebook_get_ads(
    access_token: str = settings.FACEBOOK_ACCESS_TOKEN,
) -> list[AdAccount]:
    """
        Get ad accounts from Facebook API using the provided access token.
    """
    ads_api = FacebookAdsApi.init(app_id=settings.FACEBOOK_APP_ID, app_secret=settings.FACEBOOK_APP_SECRET, access_token=access_token)
    aau = AdAccountUser("me", api=ads_api)
    ad_accounts: list[AdAccount] = aau.get_ad_accounts(fields=[
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
    ])
    for ad_account in ad_accounts:
        print(ad_account.get_ads(fields=[
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
        ]))
    return []