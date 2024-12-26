from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import (
    query
)

app = FastAPI(root_path="/query")

@app.get("/health")
async def check_health():
    return JSONResponse(content={"status": "success", "detail": "Service Available"})

app.include_router(query.router)
