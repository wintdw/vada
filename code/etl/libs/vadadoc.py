import json
from typing import Dict, Union

from libs.utils.common import remove_fields, generate_docid


class VadaDocument:
    def __init__(self, doc: Union[str, Dict]):
        if isinstance(doc, str):
            self.doc = json.loads(doc)
        elif isinstance(doc, dict):
            self.doc = doc

    def get_doc(self) -> Dict:
        return self.doc

    def get_index_name(self) -> str:
        index_name = (
            self.doc.get("_vada", {})
            .get("ingest", {})
            .get("destination", {})
            .get("index", "")
        )
        return index_name

    def get_index_friendly_name(self) -> str:
        index_friendly_name = (
            self.doc.get("_vada", {})
            .get("ingest", {})
            .get("destination", {})
            .get("index_friendly_name", "")
        )
        return index_friendly_name

    def get_user_id(self) -> str:
        user_id = self.doc.get("_vada", {}).get("ingest", {}).get("user_id", "")
        return user_id

    def set_user_id(self, user_id: str):
        self.doc["_vada"]["ingest"]["user_id"] = user_id

    def populate_ingestor_metadata(self):
        """
        This method is exclusively used by the ingestor to populate the _vada field.
        """
        if "IndexName" not in self.doc:
            raise RuntimeError("Missing required field: 'IndexName': %s", self.doc)

        index_name = self.doc["IndexName"]
        if "FriendlyName" in self.doc:
            index_friendly_name = self.doc["FriendlyName"]
        else:
            index_friendly_name = index_name

        self.doc = remove_fields(self.doc, ["IndexName", "FriendlyName"])
        doc_id = generate_docid(self.doc)

        # update _vada field
        self.doc["_vada"] = {
            "ingest": {
                "doc_id": doc_id,
                "destination": {
                    "type": "elasticsearch",
                    "index": index_name,
                    "index_friendly_name": index_friendly_name,
                },
            }
        }
