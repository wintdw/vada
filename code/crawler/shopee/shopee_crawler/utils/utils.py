import logging
import aiohttp  # type: ignore
import time
import hmac
import hashlib
import urllib.parse
from typing import Optional
from model.setting import settings


def _generate_signature(path: str, timestamp: int) -> str:
    partner_id = settings.SHOPEE_PARTNER_ID
    partner_key = settings.SHOPEE_PARTNER_KEY.encode()
    
    logging.info(
            f"Signature: {partner_id} --- {partner_key}"
    )
      
      
    base_string = f"{partner_id}{path}{timestamp}"
    
    logging.info(
            f"Path-timestamp: {path} {timestamp}"
    )
    
    return hmac.new(partner_key, base_string.encode(), hashlib.sha256).hexdigest()


def _generate_signature_shop(
    path: str,
    timestamp: int,
    access_token: str,
    shop_id: int
) -> str:
    partner_id = str(settings.SHOPEE_PARTNER_ID)
    partner_key = settings.SHOPEE_PARTNER_KEY.encode()
    parsed_shop_id = str(shop_id)
    base_string = f"{partner_id}{path}{timestamp}{access_token}{parsed_shop_id}"

    logging.info(f"[Shopee Signature] Base string: {base_string}")

    return hmac.new(partner_key, base_string.encode(), hashlib.sha256).hexdigest()

def generate_partner_signature(
    path: str,
    timestamp: int,
    access_token: str,
    shop_id: int
) -> str:

    partner_id = str(settings.SHOPEE_PARTNER_ID)
    partner_key = settings.SHOPEE_PARTNER_KEY.encode()
    base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"

    logging.info(f"[Shopee Signature - Order v2] Base string: {base_string}")

    return hmac.new(partner_key, base_string.encode(), hashlib.sha256).hexdigest()


def _get_domain(sandbox: bool) -> str:
    return settings.SHOPEE_SANDBOX_API_DOMAIN if sandbox else settings.SHOPEE_PRODUCTION_API_DOMAIN


def generate_shopee_auth_url(
    redirect_url: str,
    custom_redirect_params: Optional[dict] = None,
    sandbox: bool = False
) -> str:
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = _generate_signature(path, timestamp)
    domain = settings.SHOPEE_SANDBOX_AUTH_DOMAIN if sandbox else settings.SHOPEE_PRODUCTION_AUTH_DOMAIN

    query_params = {
        "auth_type": "seller",
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "response_type": "code",
        "sign": sign,
        "redirect": redirect_url
    }

    if custom_redirect_params:
        query_params.update(custom_redirect_params)

    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    return f"https://{domain}{path}?{query_string}"


async def get_access_token(
    authorized_code: str,
    shop_id: int,
    sandbox: bool = False
):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    sign = _generate_signature(path, timestamp)
    domain = _get_domain(sandbox)

    query = {
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }
    url = f"https://{domain}{path}?{urllib.parse.urlencode(query)}"

    payload = {
        "code": authorized_code,
        "shop_id": shop_id,
        "partner_id": settings.SHOPEE_PARTNER_ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()

async def refresh_access_token(
    refresh_token: str,
    sandbox: bool = False
):
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = _generate_signature(path, timestamp)
    domain = _get_domain(sandbox)

    query = {
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }

    url = f"https://{domain}{path}?{urllib.parse.urlencode(query)}"

    payload = {
        "refresh_token": refresh_token,
        "partner_id": settings.SHOPEE_PARTNER_ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp.raise_for_status()
            new_tokens = await resp.json()
            return new_tokens
