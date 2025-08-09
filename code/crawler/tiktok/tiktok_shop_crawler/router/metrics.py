from fastapi import APIRouter, Response  # type: ignore
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST  # type: ignore

router = APIRouter()


@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)