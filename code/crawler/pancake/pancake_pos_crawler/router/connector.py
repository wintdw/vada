from fastapi import APIRouter  # type: ignore
import logging

from model.index_mappings import index_mappings_data
from handler.crawl_info import set_crawl_info

router = APIRouter()

@router.get("/ingest/partner/pancake/pos/config")
async def expose_config():
    return {"mappings": index_mappings_data["mappings"]}

@router.post("/ingest/partner/pancake/pos/create", tags=["Connector"])
async def post_token(api_key: str, vada_uid: str):
    """
    Endpoint to save crawl info for Pancake POS.
    :param api_key: The API token for Pancake POS.
    :param vada_uid: The Vada user ID.
    :return: A dictionary with the status and message.
    """

    crawl_interval = 240  # Default crawl interval in minutes

    try:
        # Generate unique index name
        index_name = f"data_pancake_pos_{api_key[:5]}"
        friendly_index_name = f"Pancake POS - {api_key[:5]}"

        # Insert/update crawl info in database
        saved_crawl_info = await set_crawl_info(
            vada_uid=vada_uid,
            index_name=index_name,
            api_key=api_key,
            crawl_interval=crawl_interval,
        )
        logging.info(saved_crawl_info)

        return {
            "status": "success",
            "message": "Crawl info saved successfully.",
            "index_name": index_name,
            "friendly_index_name": friendly_index_name,
        }
    except Exception as e:
        logging.error(f"Error saving crawl info: {e}")
        return {
            "status": "error",
            "message": f"Failed to save crawl info: {str(e)}"
        }