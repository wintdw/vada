import hmac
import hashlib

from typing import Optional
from urllib.parse import urlparse, parse_qsl


def cal_sign(
    url: str,
    app_secret: str,
    body: Optional[bytes] = b"",
    content_type: str = "",
) -> str:
    """
    Generate the TikTok Shop API signature.

    :param url: Full request URL including query string.
    :param app_secret: TikTok Shop app secret.
    :param body: Request body as raw bytes (only for POST/PUT).
    :param content_type: Content-Type header (e.g. application/json).
    :return: HMAC-SHA256 signature string.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path

    # Parse and filter query parameters
    query_params = {
        k: v
        for k, v in parse_qsl(parsed_url.query)
        if k not in ("sign", "access_token")
    }

    # Sort and concatenate query parameters
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(query_params.items()))
    base_string = f"{path}{sorted_params}"

    # Append body if not multipart
    if content_type.lower() != "multipart/form-data" and body:
        base_string += body.decode("utf-8")

    # Final string to sign
    to_sign = f"{app_secret}{base_string}{app_secret}"

    # HMAC-SHA256 hash
    return hmac.new(
        key=app_secret.encode("utf-8"),
        msg=to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
