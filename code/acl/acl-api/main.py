from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import (
    group,
    user_group,
    group_setting,
    user_setting,
    setting,
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

app.include_router(group.router)
app.include_router(user_group.router)
app.include_router(user_setting.router)
app.include_router(group_setting.router)
app.include_router(setting.router)
