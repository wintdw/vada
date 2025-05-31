import hmac
import hashlib


def sign(path: str, query_params: dict, app_secret: str) -> str:
    """
    Generate a cryptographic HMAC-SHA256 signature for TikTok Shop API.

    Args:
        path (str): The API path, e.g., '/authorization/202309/shops'
        query_params (dict): Dictionary of query parameters
        app_secret (str): TikTok Shop App secret

    Returns:
        str: HMAC-SHA256 hex digest signature
    """
    # Step 1: Sort query parameter names alphabetically
    sorted_params = dict(sorted(query_params.items()))

    # Step 2: Concatenate the sorted parameter names and values
    concatenated_params = "".join(f"{k}{v}" for k, v in sorted_params.items())

    # Step 3: Append to the path
    base_string = f"{path}{concatenated_params}"

    # Step 4: Prepend and append the secret
    to_sign = f"{app_secret}{base_string}{app_secret}"

    # Step 5: HMAC-SHA256 encode
    signature = hmac.new(
        key=app_secret.encode("utf-8"),
        msg=to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return signature
