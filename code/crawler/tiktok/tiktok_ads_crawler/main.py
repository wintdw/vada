import logging
import asyncio

from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi_utils.tasks import repeat_every  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from routers import (
    tiktok,
    crawl_history,
    crawl_info,
    connector,
    schedule,
    index,
    metrics,
)

app = FastAPI()


@repeat_every(seconds=60)  # Executes every 1 minute, do not overlap
async def periodic_task():
    from routers.schedule import post_schedule_auth, post_schedule_crawl

    # This will take long for new crawl
    await post_schedule_auth()
    await post_schedule_crawl()


@app.get("/health")
async def check_health():
    from repositories import health_check

    try:
        await health_check()
    except Exception as e:
        logging.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Database Service Unavailable")
    return JSONResponse(content={"status": "success", "detail": "Service Available"})


app.include_router(tiktok.router)
app.include_router(crawl_history.router)
app.include_router(crawl_info.router)
app.include_router(connector.router)
app.include_router(schedule.router)
app.include_router(index.router)
app.include_router(metrics.router)
