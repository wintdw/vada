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

# Locks to prevent overlapping runs
post_schedule_auth_lock = asyncio.Lock()
post_schedule_crawl_lock = asyncio.Lock()

# Store background tasks
app.state.bg_tasks = []


@app.on_event("startup")
@repeat_every(seconds=60)  # Executes every 1 minute
async def periodic_task():
    from routers.schedule import post_schedule_auth, post_schedule_crawl

    async def safe_post_schedule_auth():
        if post_schedule_auth_lock.locked():
            logging.info("post_schedule_auth is already running, skipping this run.")
            return
        async with post_schedule_auth_lock:
            try:
                await post_schedule_auth()
            except Exception as e:
                logging.error(f"post_schedule_auth failed: {e}", exc_info=True)

    async def safe_post_schedule_crawl():
        if post_schedule_crawl_lock.locked():
            logging.info("post_schedule_crawl is already running, skipping this run.")
            return
        async with post_schedule_crawl_lock:
            try:
                await post_schedule_crawl()
            except Exception as e:
                logging.error(f"post_schedule_crawl failed: {e}", exc_info=True)

    # Save references to tasks for shutdown
    task1 = asyncio.create_task(safe_post_schedule_auth())
    task2 = asyncio.create_task(safe_post_schedule_crawl())
    app.state.bg_tasks.extend([task1, task2])


@app.on_event("shutdown")
async def shutdown_event():
    # Cancel and await all background tasks
    if hasattr(app.state, "bg_tasks"):
        for task in app.state.bg_tasks:
            task.cancel()
        for task in app.state.bg_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass


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
