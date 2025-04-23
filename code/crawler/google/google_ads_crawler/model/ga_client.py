from pydantic import BaseModel  # type: ignore


class GoogleAdsCredentials(BaseModel):
    refresh_token: str
    client_id: str = None
    client_secret: str = None
    developer_token: str = "3WREvqoZUexzpH_oDUjOPw"
    use_proto_plus: bool = True
