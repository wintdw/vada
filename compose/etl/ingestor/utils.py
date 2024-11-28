from typing import Dict, List


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


def process_msg(msg: str) -> Dict:
    """
    This function is for further processing the message input by client

    Args:
        msg (str): message from client, expected a str

    Raises:
        json.JSONDecodeError: if parse error, or no IndexName field present

    Returns:
        Dict: A json object, with __meta field
    """
    json_msg = json.loads(msg)

    if not isinstance(json_msg, dict):
        raise json.JSONDecodeError(
            "Expected a JSON object (dictionary)", doc=json_msg, pos=0
        )

    if "IndexName" not in json_msg:
        raise json.JSONDecodeError("Missing IndexName field", doc=json_msg, pos=0)

    # move IndexName to meta
    json_msg["__meta"] = {"index_name": json_msg["IndexName"]}
    # will be correct
    if "FiendlyName" in json_msg:
        json_msg["__meta"]["index_friendly_name"] = json_msg["FiendlyName"]
    elif "FriendlyName" in json_msg:
        json_msg["__meta"]["index_friendly_name"] = json_msg["FriendlyName"]

    ret_msg = remove_fields(json_msg, ["IndexName", "FiendlyName", "FriendlyName"])

    return ret_msg
