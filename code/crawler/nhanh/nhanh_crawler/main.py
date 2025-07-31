import asyncio
import logging
from fastapi import FastAPI  # type: ignore

from router import connector, schedule, metrics
from scheduler.main import init_scheduler


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


app = FastAPI()


@app.get("/health")
async def check_health():
    return {"status": "success", "detail": "Service Available"}


app.include_router(metrics.router)
app.include_router(connector.router)
app.include_router(schedule.router)


async def init_scheduler_background():
    scheduler = await init_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler


@app.on_event("startup")
async def startup_event():
    # Create background task for scheduler initialization
    app.state.scheduler_task = asyncio.create_task(init_scheduler_background())


@app.on_event("shutdown")
async def shutdown_event():
    # 1. Stop the scheduler if it exists
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()

    # 2. Cancel the background initialization task
    if hasattr(app.state, "scheduler_task"):
        app.state.scheduler_task.cancel()  # Request cancellation
        try:
            await app.state.scheduler_task  # Wait for task to complete
        except asyncio.CancelledError:
            pass  # Suppress the cancellation error
