import json
import hashlib
from typing import Dict, List


def generate_docid(doc: Dict) -> str:
    serialized_data = json.dumps(doc, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}
