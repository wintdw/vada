from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from routers import (
    tiktok,
    crawl_history,
    crawl_info,
    connector,
    schedule
)

app = FastAPI()

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
@repeat_every(seconds=3600)  # Executes every 60 minutes
async def periodic_task() -> None:
    from routers.schedule import post_schedule_auth, post_schedule_crawl

    await post_schedule_auth()
    await post_schedule_crawl()

@app.on_event("startup")
@repeat_every(seconds=60)  # Executes every 1 minute
async def update_metrics() -> None:
    from tools import update_metrics

    await update_metrics()

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
app.include_router(crawl_history.router)
app.include_router(crawl_info.router)
app.include_router(connector.router)
app.include_router(schedule.router)