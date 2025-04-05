from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import (
    tiktok
)

app = FastAPI()

@app.get("/health")
async def check_health():
    from repositories import health_check

    try:
        await health_check()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="Database Service Unavailable"
        )
    return JSONResponse(content={"status": "success", "detail": "Service Available"})

app.include_router(tiktok.router)
