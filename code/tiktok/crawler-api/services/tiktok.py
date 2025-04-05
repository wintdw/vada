from tools import get, post, put
from tools.settings import settings

async def tiktok_biz_get_advertiser():
    request_json = await get(
        url = f"{settings.TIKTOK_BIZ_API_URL}/oauth2/advertiser/get/",
        access_token = settings.TIKTOK_BIZ_ACCESS_TOKEN,
        params = {"app_id": settings.TIKTOK_BIZ_APP_ID, "secret": settings.TIKTOK_BIZ_SECRET}
    )
    return request_json
