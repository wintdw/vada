import logging
from fastapi import FastAPI, Depends

from api.routers import health, mappings, users
from .dependencies import get_mappings_processor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger().setLevel(logging.INFO)

app = FastAPI()


@app.on_event("startup")
async def startup():
    pass


@app.on_event("shutdown")
async def shutdown():
    pass


app.include_router(health.router)
app.include_router(mappings.router, dependencies=[Depends(get_mappings_processor)])
# app.include_router(users.router)
