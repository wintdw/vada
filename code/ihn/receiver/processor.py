import os
import json
import logging
import aiofiles  # type: ignore
from datetime import datetime
from typing import Dict
from fastapi import HTTPException, status  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from libs.async_es import AsyncESProcessor


class AsyncProcessor:
    def __init__(self, es_conf_dict: Dict):
        self.es = AsyncESProcessor(
            es_conf_dict["url"], es_conf_dict["user"], es_conf_dict["passwd"]
        )

    async def persist_to_file(self, output_dir: str, json_data: Dict):
        os.makedirs(output_dir, exist_ok=True)

        table_fullname = json_data.get("table_fullname")
        if not table_fullname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'table_fullname' in the request data",
            )

        date_str = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(output_dir, f"{table_fullname}_{date_str}.json")

        try:
            async with aiofiles.open(file_path, "a", encoding="utf-8") as file:
                await file.write(json.dumps(json_data) + "\n")
            return JSONResponse(content={"detail": "Data captured successfully!"})
        except Exception as e:
            logging.error("Failed to write data to %s, %s", file_path, e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
