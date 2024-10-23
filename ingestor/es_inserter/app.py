import os
import json
import hashlib
import logging
from aiohttp import ClientSession, ClientResponse, BasicAuth
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List


app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
ELASTIC_USER = "elastic"
ELASTIC_PASSWD = ""
ELASTIC_URL = "http://demo.internal.vadata.vn:9200"
# Passwd
elastic_passwd_file = os.getenv('ELASTIC_PASSWD_FILE')
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, 'r') as file:
        ELASTIC_PASSWD = file.read().strip()


def generate_docid(msg: Dict) -> str:
    serialized_data = json.dumps(msg, sort_keys=True)
    return hashlib.sha256(serialized_data.encode('utf-8')).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


async def send_to_es(index_name: str, doc_id: str, msg: Dict) -> ClientResponse:
    es_user = ELASTIC_USER
    es_pass = ELASTIC_PASSWD
    es_url = f"{ELASTIC_URL}/{index_name}/_doc/{doc_id}"
    
    async with ClientSession() as session:
        async with session.put(es_url, 
                               json=msg, 
                               auth=BasicAuth(es_user, es_pass)) as response:
            logging.debug(f"Index: {index_name}")
            if response.status == 201:
                logging.debug("Document created successfully")
            elif response.status == 200:
                logging.debug("Document updated successfully")
            else:
                logging.error(f"Failed to send data to Elasticsearch. Status code: {response.status}")
                logging.error(await response.text())
    
    return response


async def check_es_health() -> ClientResponse:
    es_user = ELASTIC_USER
    es_pass = ELASTIC_PASSWD
    es_url = f"{ELASTIC_URL}/_cluster/health"

    async with ClientSession() as session:
        async with session.get(es_url, auth=BasicAuth(es_user, es_pass)) as response:
            if response.status == 200:
                health_info = await response.json()
            else:
                logging.error(f"Failed to get health info: {response.status} - {await response.text()}")

    return response

@app.get("/health")
async def check_health():
    response = await check_es_health()

    if response.status < 400:
        return JSONResponse(content={"status": "success", "detail": "Service Available"})
    else:
        return JSONResponse(content={"status": "error", "detail": f"{response.text}"}, status_code=500)


# This function can deal with duplicate messages
@app.post("/jsonl")
async def receive_jsonl(request: Request):
    try:
        body = await request.body()
        json_lines = body.decode('utf-8').splitlines()

        count = 0
        for line in json_lines:
            event = json.loads(line)
            # Check for required index_name
            if not event["index_name"]:
                raise HTTPException(status_code=400, detail="Missing index_name")

            index_name = event["index_name"]
            doc = remove_fields(event, ["index_name", "__meta"])
            doc_id = generate_docid(doc)
            logging.debug(doc)

            response = await send_to_es(index_name, doc_id, doc)
            if response.status not in {200, 201}:
                raise HTTPException(status_code=response.status, detail=response.text())
            
            count += 1

        return JSONResponse(content={"status": "success", "detail": f"{count} messages successfully written"})

    except Exception as e:
        logging.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)