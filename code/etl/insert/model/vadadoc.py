import json
import re
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
        try:
            index_name = (
                self.doc.get("_vada", {})
                .get("ingest", {})
                .get("destination", {})
                .get("index", "")
            )
            return index_name
        except AttributeError:
            raise ValueError(
                f"Document does not contain a valid _vada field: {self.doc}"
            )

    def get_index_friendly_name(self) -> str:
        try:
            index_friendly_name = (
                self.doc.get("_vada", {})
                .get("ingest", {})
                .get("destination", {})
                .get("index_friendly_name", "")
            )
            return index_friendly_name
        except AttributeError:
            raise ValueError(
                f"Document does not contain a valid _vada field: {self.doc}"
            )

    def get_user_id(self) -> str:
        try:
            user_id = self.doc.get("_vada", {}).get("ingest", {}).get("user_id", "")
            return user_id
        except AttributeError:
            raise ValueError(
                f"Document does not contain a valid _vada field: {self.doc}"
            )

    def populate_ingestor_metadata(
        self, user_id: str, index_name: str, index_friendly_name: str = ""
    ):
        """
        This method is exclusively used by the ingestor to populate the _vada field.
        """
        if not index_friendly_name:
            index_friendly_name = index_name
        if index_friendly_name == index_name:
            # pretify the index_friendly_name
            match = re.search(r"csv_(.*?)_csv", index_name)
            if match:
                index_friendly_name = f"CSV " + match.group(1)

        # TODO: remove
        self.doc = remove_fields(self.doc, ["IndexName", "FriendlyName"])

        doc_id = generate_docid(self.doc)

        # update _vada field
        self.doc["_vada"] = {
            "ingest": {
                "user_id": user_id,
                "doc_id": doc_id,
                "destination": {
                    "type": "elasticsearch",
                    "index": index_name,
                    "index_friendly_name": index_friendly_name,
                },
            }
        }
