from fastapi import APIRouter  # type: ignore

from model.index_mappings import index_mappings_data

router = APIRouter()

@router.get("/ingest/partner/pancake/pos/config")
async def expose_config():
    return {"mappings": index_mappings_data["mappings"]}
