import json

def create_report(
    advertiser_info: dict,
    report_integrated: dict,
    ad: dict,
    campaign: dict,
    adgroup: dict,
) -> dict:
    return advertiser_info.get("data").get("list")[0] | report_integrated.get("data").get("list")[0] | ad.get("data").get("list")[0] | campaign.get("data").get("list")[0] | adgroup.get("data").get("list")[0]

def save_report(data, filename):
  with open(filename, 'a', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
    f.write('\n')
