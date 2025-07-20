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


@app.on_event("startup")
@repeat_every(seconds=60)  # Executes every 1 minute, do not overlap
async def periodic_task():
    from routers.schedule import post_schedule_auth, post_schedule_crawl

    # Clean up completed tasks
    if hasattr(app.state, "bg_tasks"):
        app.state.bg_tasks = [task for task in app.state.bg_tasks if not task.done()]
    else:
        app.state.bg_tasks = []

    auth_task = asyncio.create_task(post_schedule_auth())
    crawl_task = asyncio.create_task(post_schedule_crawl())

    app.state.bg_tasks.extend([auth_task, crawl_task])


@app.on_event("shutdown")
async def shutdown():
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
