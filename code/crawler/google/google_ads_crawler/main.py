import os
import logging
from fastapi import FastAPI  # type: ignore
from router import auth, account, report
from scheduler.get_reports import init_scheduler

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Google Ads Crawler")

# Store the flow object in a global variable or use a more robust solution like a database in production
flows = {}

app.include_router(auth.router, tags=["auth"])
app.include_router(account.router, tags=["account"])
app.include_router(report.router, tags=["report"])

# Pass the flows dictionary to router endpoints that need it
app.state.flows = flows


##### SCHEDULER #####
# Initialize and start the scheduler
scheduler = init_scheduler()


@app.on_event("startup")
async def startup_event():
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
