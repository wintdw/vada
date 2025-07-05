from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi.responses import JSONResponse

from routers import (
    connector,
#    schedule,
    metrics
)

app = FastAPI()
"""
@app.on_event("startup")
@repeat_every(seconds=60)  # Executes every 1 minute
async def periodic_task() -> None:
    from routers.schedule import post_schedule_auth, post_schedule_crawl

    await post_schedule_auth()
    await post_schedule_crawl()
"""
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

app.include_router(connector.router)
#app.include_router(schedule.router)
app.include_router(metrics.router)
