import os
import jwt
import logging
from typing import Dict
from fastapi import Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore

from api.models import JWTPayload


# Support TOKEN_SECRET_FILE to read secret from environment variable
TOKEN_SECRET = ""
token_secret_file = os.getenv("TOKEN_SECRET_FILE", "")
if token_secret_file and os.path.isfile(token_secret_file):
    with open(token_secret_file, "r", encoding="utf-8") as file:
        TOKEN_SECRET = file.read().strip()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
