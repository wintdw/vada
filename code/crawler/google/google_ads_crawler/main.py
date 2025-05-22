import os
import logging
from fastapi import FastAPI  # type: ignore

from router import auth, account, report, metric, config
from scheduler.get_reports import init_scheduler

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Google Ads Crawler")

# Store the flow object in a global variable or use a more robust solution like a database in production
flows = {}

app.include_router(config.router)
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(report.router)
app.include_router(metric.router)

# Pass the flows dictionary to router endpoints that need it
app.state.flows = flows


@app.on_event("startup")
async def startup_event():
    scheduler = await init_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler  # Store scheduler in app.state


@app.on_event("shutdown")
async def shutdown_event():
    app.state.scheduler.shutdown()  # Access scheduler from app.state
