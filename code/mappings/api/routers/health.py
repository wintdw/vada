from fastapi import APIRouter  # type: ignore

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "detail": "Service Available"}
