# pylint: disable=import-error,wrong-import-position

import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

# custom libs
from libs.connectors.async_kafka import AsyncKafkaProcessor
from libs.connectors.mappings import MappingsClient

from etl.libs.processor import get_kafka_processor, get_mappings_client
from etl.ingest.handler.process import process
from etl.ingest.model.ingest import IngestRequest

app = FastAPI()
# asyncio.get_event_loop().set_debug(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

APP_ENV = os.getenv("APP_ENV")


@app.get("/health")
async def check_health(
    mappings_client: MappingsClient = Depends(get_mappings_client),
):
    """Check the health of Mappings service."""
    mappings_response = await mappings_client.check_health()

    if mappings_response["status"] < 400:
        return JSONResponse(content={"status": "available"})
    else:
        logging.error(mappings_response["detail"])

    raise HTTPException(
        status_code=mappings_response["status"],
        detail=mappings_response["detail"],
    )


@app.post("/v1/json")
async def handle_json(
    request: IngestRequest,
    kafka_processor: AsyncKafkaProcessor = Depends(get_kafka_processor),
    mappings_client: MappingsClient = Depends(get_mappings_client),
):
    """Accept JSON data with meta information and data array.

    Format:
    {
        "meta": {
            "user_id": str,
            "index_name": str,
            "index_friendly_name": str (optional)
        },
        "data": List[Dict]
    }
    """
    try:
        response = await process(
            kafka_processor=kafka_processor,
            mappings_client=mappings_client,
            data=request.data,
            app_env=APP_ENV,
            user_id=request.meta.user_id,
            index_name=request.meta.index_name,
            index_friendly_name=request.meta.index_friendly_name,
        )

        return JSONResponse(content=response)

    except RuntimeError as run_err:
        logging.error("Runtime error: %s", str(run_err))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(run_err)
        )
    except Exception as e:
        logging.error("Error processing request: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing request: {str(e)}",
        )
    finally:
        await kafka_processor.close()
