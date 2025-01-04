import os
import json
import logging
import aiofiles  # type: ignore
from datetime import datetime
from typing import Dict
from fastapi import HTTPException, status  # type: ignore

import libs.utils
from libs.async_es import AsyncESProcessor


class AsyncProcessor:
    def __init__(self, es_conf_dict: Dict):
        self.es = AsyncESProcessor(
            es_conf_dict["url"], es_conf_dict["user"], es_conf_dict["passwd"]
        )

    async def persist_to_file(self, output_dir: str, json_data: Dict):
        """
        Persist the whole message to file, including metadata
        """
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
        except Exception as e:
            logging.error("Failed to write data to %s, %s", file_path, e)

    async def persist_to_es(self, index: str, json_data: Dict):
        """
        The json_data is in the format of json_data["data"]: List[Dict]
        The List is the actual data that we need to send to ES
        """
        data_list = json_data.get("data", [])
        if not data_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'data' in the request data",
            )

        success_count = 0
        failure_count = 0

        for row in data_list:
            doc_id = libs.utils.generate_docid(row)
            try:
                await self.es.send_to_es(index, doc_id, row)
                success_count += 1
            except Exception as e:
                logging.error("Failed to index data to ES, %s", e)
                failure_count += 1
                continue

        logging.info("Success: %d docs, Failure: %d docs", success_count, failure_count)
