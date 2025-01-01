import os
import logging
from libs.crm import CRMAPI
import pytest  # type: ignore

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CRM_BASEURL = os.getenv("CRM_BASEURL", "https://dev-crm-api.vadata.vn")
CRM_USER = ""
CRM_PASS = ""
passwd_file = os.getenv("CRM_PASSWD_FILE", "")
if passwd_file and os.path.isfile(passwd_file):
    with open(passwd_file, "r", encoding="utf-8") as file:
        content = file.read().strip()
        CRM_USER, CRM_PASS = content.split(maxsplit=1)


@pytest.mark.asyncio
async def test_login():
    api = CRMAPI(CRM_BASEURL)
    await api.auth(CRM_USER, CRM_PASS)
    assert "Authorization" in api.headers
    assert api.headers["Authorization"].startswith("Bearer ")


@pytest.mark.asyncio
async def test_check_index_created():
    api = CRMAPI(CRM_BASEURL)
    await api.auth(CRM_USER, CRM_PASS)
    index = "demo_sale_data"
    response = await api.check_index_created(index)
    assert response is not None
    assert isinstance(response, dict)
