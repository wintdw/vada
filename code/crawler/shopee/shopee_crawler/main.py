import asyncio
import logging
from fastapi import FastAPI  # type: ignore

from router import auth, config
from scheduler.main import init_scheduler
from init_db import main as init_database


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Shopee Crawler")

app.include_router(auth.router)
app.include_router(config.router)


async def init_scheduler_background():
    scheduler = await init_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler


@app.on_event("startup")
async def startup_event():
    # Initialize database tables first
    logging.info("🔧 Initializing database...")
    await init_database()
    
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
