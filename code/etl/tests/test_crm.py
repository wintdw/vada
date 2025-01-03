import os
import pytest  # type: ignore
import logging
from libs.crm import CRMAPI

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CRM_BASEURL = os.getenv("CRM_BASEURL", "https://dev-crm-api.vadata.vn")
CRM_USER = ""
CRM_PASS = ""
passwd_file = os.getenv("CRM_PASSWD_FILE", "/var/secret/docker/crm/user7500")
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

    # Test failed login
    invalid_user = "invalid_user"
    invalid_pass = "invalid_pass"
    with pytest.raises(Exception) as excinfo:
        await api.auth(invalid_user, invalid_pass)
    assert "Failed to authenticate user" in str(excinfo.value)


@pytest.mark.asyncio
async def test_check_index_created():
    api = CRMAPI(CRM_BASEURL)
    await api.auth(CRM_USER, CRM_PASS)
    index = "demo_sale_data"
    response = await api.check_index_created(index)
    assert isinstance(response, dict)


@pytest.mark.asyncio
async def test_is_auth():
    api = CRMAPI(CRM_BASEURL)
    await api.auth(CRM_USER, CRM_PASS)
    assert await api.is_auth() is True

    # Invalidate the token by modifying the headers
    api.headers["Authorization"] = "Bearer invalid_token"
    assert await api.is_auth() is False
