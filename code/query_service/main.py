from fastapi import FastAPI  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from routers import query

app = FastAPI()


@app.get("/health")
async def check_health():
    return JSONResponse(content={"status": "success", "detail": "Service Available"})

app.include_router(query.router)
