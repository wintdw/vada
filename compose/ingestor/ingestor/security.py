import jwt
import logging
from typing import Dict

from fastapi.security import OAuth2PasswordBearer
from basemodels import JWTPayload


TOKEN_SECRET = ""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def verify_jwt(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=["HS256"])
        logging.debug(f"Authenticated as {payload.get('name')}")

        # Convert payload to JWTPayload model for validation
        JWTPayload(**payload)

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token"
        )
