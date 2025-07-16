import hmac
import hashlib

from typing import Optional, Dict, Any


def cal_sign(
    path: str,
    params: Dict[str, Any],
    app_secret: str,
    body: Optional[bytes] = b"",
    content_type: str = "",
) -> str:
    """
    Generate the TikTok Shop API signature.

    :param path: API path, e.g. "/api/orders/search".
    :param params: Query parameters (excluding 'sign' and 'access_token').
    :param app_secret: TikTok Shop app secret.
    :param body: Request body as raw bytes (used for POST/PUT).
    :param content_type: Content-Type header.
    :return: HMAC-SHA256 signature string.
    """
    # Filter out 'sign' and 'access_token' if included
    filtered_params = {
        k: v for k, v in params.items() if k not in ("sign", "access_token")
    }

    # Sort and concatenate query parameters
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(filtered_params.items()))
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
