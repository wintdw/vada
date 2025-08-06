import os
import logging
import asyncio  # Add this import at the top
from fastapi import FastAPI  # type: ignore

from router import auth, crawl, metric, config
from scheduler.main import init_scheduler

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Google Ads Crawler")

# Store the flow object in a global variable or use a more robust solution like a database in production
flows = {}

app.include_router(config.router)
app.include_router(auth.router)
app.include_router(crawl.router)
app.include_router(metric.router)

# Pass the flows dictionary to router endpoints that need it
app.state.flows = flows


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
