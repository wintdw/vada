import aiohttp  # type: ignore


async def get(
    url: str,
    bearer_token: str = "",
    access_token: str = "",
    params: dict = {},
    headers: dict = {},
) -> dict:
    if not headers:
        headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif access_token:
        headers["Access-Token"] = f"{access_token}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            status = response.status
            request_json = await response.json()
            if status != 200:
                raise Exception(
                    f"Request to {url} failed with status {status}: {request_json}"
                )
            else:
                return request_json


async def put(
    url: str,
    json: dict,
    bearer_token: str = "",
    access_token: str = "",
    params: dict = {},
    headers: dict = {},
) -> dict:
    if not headers:
        headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif access_token:
        headers["Access-Token"] = f"{access_token}"
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, json=json, headers=headers, params=params
        ) as response:
            status = response.status
            request_json = await response.json()
            if status != 200:
                raise Exception(
                    f"Request to {url} failed with status {status}: {request_json}"
                )
            else:
                return request_json


async def post(
    url: str,
    json: dict,
    bearer_token: str = "",
    access_token: str = "",
    params: dict = {},
    headers: dict = {},
) -> dict:
    if not headers:
        headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif access_token:
        headers["Access-Token"] = f"{access_token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=json, headers=headers, params=params
        ) as response:
            status = response.status
            request_json = await response.json()
            if status != 200:
                raise Exception(
                    f"Request to {url} failed with status {status}: {request_json}"
                )
            else:
                return request_json
