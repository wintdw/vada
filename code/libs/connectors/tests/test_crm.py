"""
Test by:
# export CRM_BASEURL=https://dev-crm-api.vadata.vn; export CRM_PASSWD_FILE=/var/secret/docker/crm/user7500.passwd; python3 -m pytest -s -vvv libs/connectors/
"""

import os
import time
import logging
import pytest  # type: ignore

from libs.connectors.crm import CRMAPI

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CRM_BASEURL = os.getenv("CRM_BASEURL", "")
CRM_USER = os.getenv("CRM_USER", "")
CRM_PASS = os.getenv("CRM_PASS", "")
passwd_file = os.getenv("CRM_PASSWD_FILE", "")
if passwd_file and os.path.isfile(passwd_file):
    with open(passwd_file, "r", encoding="utf-8") as file:
        content = file.read().strip()
        CRM_USER, CRM_PASS = content.split(maxsplit=1)


@pytest.mark.asyncio
async def test_health():
    api = CRMAPI(CRM_BASEURL)
    try:
        await api.auth(CRM_USER, CRM_PASS)

        response = await api.check_health()

        assert response[0] == 200
        assert response[1].get("message") == "pong"
    finally:
        await api.close()


@pytest.mark.asyncio
async def test_login():
    api = CRMAPI(CRM_BASEURL)
    try:
        await api.auth(CRM_USER, CRM_PASS)
        assert "Authorization" in api.headers
        assert api.headers["Authorization"].startswith("Bearer ")

        # Test failed login
        invalid_user = "invalid_user"
        invalid_pass = "invalid_pass"
        with pytest.raises(Exception) as excinfo:
            await api.auth(invalid_user, invalid_pass)
        assert "Failed to authenticate user" in str(excinfo.value)
    finally:
        await api.close()


@pytest.mark.asyncio
async def test_check_index_created():
    api = CRMAPI(CRM_BASEURL)
    try:
        await api.auth(CRM_USER, CRM_PASS)
        index = "demo_sale_data"

        start_time = time.time()
        response = await api.check_index_created(index)
        end_time = time.time()

        assert isinstance(response, dict)
        assert response.get("index", "").get("name", "") == index
        print(f"Time taken for API call: {end_time - start_time} seconds")
    finally:
        await api.close()


@pytest.mark.asyncio
async def test_check_index_notfound():
    api = CRMAPI(CRM_BASEURL)
    try:
        await api.auth(CRM_USER, CRM_PASS)
        index = "non_existent_index"

        response = await api.check_index_created(index)
        assert response == {}
    finally:
        await api.close()


@pytest.mark.asyncio
async def test_is_auth():
    api = CRMAPI(CRM_BASEURL)
    try:
        await api.auth(CRM_USER, CRM_PASS)
        assert await api.is_auth() is True

        # Invalidate the token by modifying the headers
        api.headers["Authorization"] = "Bearer invalid_token"
        assert await api.is_auth() is False
    finally:
        await api.close()
