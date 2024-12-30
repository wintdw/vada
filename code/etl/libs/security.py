import os
import jwt
import logging
import asyncio
import aiohttp
from typing import Dict
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


# Support TOKEN_SECRET_FILE to read secret from environment variable
TOKEN_SECRET = ""
token_secret_file = os.getenv("TOKEN_SECRET_FILE", "")
if token_secret_file and os.path.isfile(token_secret_file):
    with open(token_secret_file, "r", encoding="utf-8") as file:
        TOKEN_SECRET = file.read().strip()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class JWTPayload(BaseModel):
    name: str
    id: str
    exp: int

    class Config:
        json_schema_extra = {
            "example": {
                "name": "user7500",
                "id": "65422b6aa2bbacc10b7a22a3",
                "exp": 1731306868,
            }
        }


async def get_access_token():
    """
    Function to call the login API and extract the access token.

    Returns:
        str: The access token from the response.
    """
    url = "https://dev-crm-api.vadata.vn/auth/login"
    payload = {"username": "user7500", "password": "smRmUd9fhhsSH8nT"}
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                access_token = data.get("access_token")
                logging.debug("Access token retrieved: %s", access_token)
                return access_token
            else:
                logging.error(
                    "Failed to retrieve access token, status code: %d", response.status
                )
                return None


def verify_jwt(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Function to verify the JWT Token header from client

    Args:
        token (str, optional): the JWT token provided. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: 401 upon Expired or Invalid tokens

    Returns:
        Dict: The decoded JWT info, and the original token
    """
    try:
        payload = jwt.decode(
            token, TOKEN_SECRET, algorithms=["HS256"], options={"verify_exp": True}
        )
        # Add original token to payload further processing
        payload["jwt"] = token
        logging.debug("Authenticated as %s", payload.get("name"))

        # Convert payload to JWTPayload model for validation
        JWTPayload(**payload)

        return payload

    except jwt.ExpiredSignatureError as exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token has expired"
        ) from exp
    except jwt.InvalidTokenError as inv:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token"
        ) from inv
