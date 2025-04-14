import json
import hashlib

def create_report(
    advertiser_info: dict,
    report_integrated: dict,
    ad: dict,
    campaign: dict,
    adgroup: dict,
) -> dict | None:
    data = report_integrated.get("data").get("list")[0]
    if all(v != "0" for v in data["metrics"].values()):
        return data["dimensions"] | data["metrics"] | {"advertiser": advertiser_info.get("data").get("list")[0]} | {"ad": ad.get("data").get("list")[0]} | {"campaign": campaign.get("data").get("list")[0]} | {"adgroup": adgroup.get("data").get("list")[0]}
    else:
        return None

def save_report(data, filename):
  with open(filename, 'a', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
    f.write('\n')

def generate_doc_id(data: dict) -> str:
    serialized_data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()

def enrich_report(report: dict, doc_id: str, index_name: str) -> dict:
    metadata = {
      "_vada": {
        "ingest": {
          "source": "crawling:tiktok_ad_detailed",
          "destination": {
            "type": "elasticsearch",
            "index": index_name
          },
          "vada_client_id": "a_quang_nguyen",
          "type": "tiktok_ad_detailed",
          "doc_id": doc_id
        }
      }
    }
    return report | metadata
