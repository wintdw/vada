import os
import logging
from fastapi import FastAPI  # type: ignore
from router import auth, account  # type: ignore

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Google OAuth API")

# Store the flow object in a global variable or use a more robust solution like a database in production
flows = {}

app.include_router(auth.router, tags=["auth"])
app.include_router(account.router, tags=["account"])
# app.include_router(report.router, tags=["report"])

# Pass the flows dictionary to router endpoints that need it
app.state.flows = flows
