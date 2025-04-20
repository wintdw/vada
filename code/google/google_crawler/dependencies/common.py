import os
from fastapi import Request, HTTPException  # type: ignore


async def get_flows(request: Request):
    """Get flows from application state"""
    return request.app.state.flows


async def get_app_secret_file():
    """Get Google app secret file path from environment variable"""
    secret_path = os.getenv("GOOGLE_APP_SECRET_FILE")
    if not secret_path:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_APP_SECRET_FILE environment variable is not set",
        )

    if not os.path.exists(secret_path):
        raise HTTPException(
            status_code=500, detail=f"Secret file not found at: {secret_path}"
        )

    return secret_path
