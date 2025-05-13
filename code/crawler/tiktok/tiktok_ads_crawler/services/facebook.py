from tools.settings import settings
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountuser import AdAccountUser

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
    return ad_accounts