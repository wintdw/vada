import os
import json
import hashlib
import logging
from aiohttp import ClientSession, ClientResponse, BasicAuth
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List


app = FastAPI()
logging.basicConfig(level=logging.INFO)
ELASTIC_URL = "http://demo.internal.vadata.vn:9200"
# Passwd
elastic_passwd_file = os.getenv('ELASTIC_PASSWD_FILE')
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, 'r') as file:
        ELASTIC_PASSWD = file.read().strip()
else:
    ELASTIC_PASSWD = ""


def generate_docid(msg: Dict) -> str:
    serialized_data = json.dumps(msg, sort_keys=True)
    return hashlib.sha256(serialized_data.encode('utf-8')).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


async def send_to_es(index_name: str, doc_id: str, msg: Dict) -> ClientResponse:
    es_user = "elastic"
    es_pass = ELASTIC_PASSWD
    es_url = f"{ELASTIC_URL}/{index_name}/_doc/{doc_id}"
    
    async with ClientSession() as session:
        async with session.put(es_url, 
                               json=msg, 
                               auth=BasicAuth(es_user, es_pass)) as response:
            if response.status == 201:
                logging.info("Document created successfully.")
            elif response.status == 200:
                logging.info("Document updated successfully.")
            else:
                logging.error(f"Failed to send data to Elasticsearch. Status code: {response.status}")
                logging.error(await response.text())
    
    return response
        

@app.post("/jsonl")
async def receive_logs(request: Request):
    try:
        body = await request.body()
        json_lines = body.decode('utf-8').splitlines()

        for line in json_lines:
            event = json.loads(line)
            # Check for required index_name
            if not event["index_name"]:
                raise HTTPException(status_code=400, detail="Missing index_name")

            index_name = event["index_name"]
            doc = remove_fields(event, ["index_name", "__meta"])
            doc_id = generate_docid(doc)
            logging.info(doc)

            response = await send_to_es(index_name, doc_id, doc)

            # Check response from Elasticsearch
            if response.status not in {200, 201}:
                raise HTTPException(status_code=response.status, detail=response.json())

            return JSONResponse(content={"status": "success", "docid": doc_id})

    except Exception as e:
        logging.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)