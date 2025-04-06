from tools import get, post, put
from tools.settings import settings

async def tiktok_biz_get_advertiser():
    request_json = await get(
        url = f"{settings.TIKTOK_BIZ_API_URL}/oauth2/advertiser/get/",
        access_token = settings.TIKTOK_BIZ_ACCESS_TOKEN,
        params = {"app_id": settings.TIKTOK_BIZ_APP_ID, "secret": settings.TIKTOK_BIZ_SECRET}
    )
    return request_json

async def tiktok_biz_info_advertiser(params: dict):
    request_json = await get(
        url = f"{settings.TIKTOK_BIZ_API_URL}/advertiser/info/",
        access_token = settings.TIKTOK_BIZ_ACCESS_TOKEN,
        params = params
    )
    return request_json

async def tiktok_biz_get_campaign(params: dict):
    request_json = await get(
        url = f"{settings.TIKTOK_BIZ_API_URL}/campaign/get/",
        access_token = settings.TIKTOK_BIZ_ACCESS_TOKEN,
        params = params
    )
    return request_json

async def tiktok_biz_get_report_integrated(params: dict):
    request_json = await get(
        url = f"{settings.TIKTOK_BIZ_API_URL}/report/integrated/get/",
        access_token = settings.TIKTOK_BIZ_ACCESS_TOKEN,
        params = params
    )
    return request_json

async def tiktok_biz_get_ad(params: dict):
    request_json = await get(
        url = f"{settings.TIKTOK_BIZ_API_URL}/ad/get/",
        access_token = settings.TIKTOK_BIZ_ACCESS_TOKEN,
        params = params
    )
    return request_json

async def tiktok_biz_get_adgroup(params: dict):
    request_json = await get(
        url = f"{settings.TIKTOK_BIZ_API_URL}/adgroup/get/",
        access_token = settings.TIKTOK_BIZ_ACCESS_TOKEN,
        params = params
    )
    return request_json
