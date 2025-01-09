from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import health, mappings, users

app = FastAPI()

app.include_router(health.router)
app.include_router(mappings.router)
app.include_router(users.router)
