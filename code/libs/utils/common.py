from typing import Dict, List


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}
