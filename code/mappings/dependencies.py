import os

from api.internals.mappings import MappingsProcessor


ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = ""
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r", encoding="utf-8") as file:
        ELASTIC_PASSWD = file.read().strip()

CRM_BASEURL = os.getenv("CRM_BASEURL", "https://dev-crm-api.vadata.vn")
CRM_USER = ""
CRM_PASS = ""
passwd_file = os.getenv("CRM_PASSWD_FILE", "")
if passwd_file and os.path.isfile(passwd_file):
    with open(passwd_file, "r", encoding="utf-8") as file:
        content = file.read().strip()
        CRM_USER, CRM_PASS = content.split(maxsplit=1)


def get_mappings_processor():
    es_conf_dict = {"url": ELASTIC_URL, "user": ELASTIC_USER, "passwd": ELASTIC_PASSWD}
    crm_conf_dict = {
        "auth": {"username": CRM_USER, "password": CRM_PASS},
        "baseurl": CRM_BASEURL,
    }
    mappings_processor = MappingsProcessor(es_conf_dict, crm_conf_dict)
    return mappings_processor
