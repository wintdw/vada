# pylint: disable=import-error,wrong-import-position


import jwt
import logging
from typing import Dict
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


TOKEN_SECRET = ""

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


def verify_jwt(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Function to verify the JWT Token header from client

    Args:
        token (str, optional): the JWT token provided. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: 401 upon Expired or Invalid tokens

    Returns:
        Dict: The decoded JWT info
    """
    try:
        payload = jwt.decode(
            token, TOKEN_SECRET, algorithms=["HS256"], options={"verify_exp": True}
        )
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
