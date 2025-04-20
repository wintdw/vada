import os
import logging
from fastapi import FastAPI

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Google OAuth API")

# Store the flow object in a global variable or use a more robust solution like a database in production
flows = {}
