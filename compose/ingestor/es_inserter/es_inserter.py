import os
import json
import logging
import traceback
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse

import utils


app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


ELASTIC_URL = os.getenv("ELASTIC_URL", "")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWD = ""
# Passwd
elastic_passwd_file = os.getenv("ELASTIC_PASSWD_FILE", "")
if elastic_passwd_file and os.path.isfile(elastic_passwd_file):
    with open(elastic_passwd_file, "r") as file:
        ELASTIC_PASSWD = file.read().strip()


@app.get("/health")
async def check_health():
    response = await utils.check_es_health(ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD)

    if response.status < 400:
        return JSONResponse(
            content={"status": "success", "detail": "Service Available"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": f"{response.text}"},
        )


# This function can deal with duplicate messages
@app.post("/jsonl")
async def receive_jsonl(request: Request):
    try:
        body = await request.body()
        json_lines = body.decode("utf-8").splitlines()

        count = 0
        for line in json_lines:
            event = json.loads(line)
            # Check for required index_name
            if not event["index_name"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Missing index_name"
                )

            index_name = event["index_name"]
            doc = utils.remove_fields(event, ["index_name", "__meta"])
            doc_id = utils.generate_docid(doc)
            logging.debug(doc)

            response = await utils.send_to_es(
                ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWD, index_name, doc_id, doc
            )
            if response.status not in {200, 201}:
                raise HTTPException(status_code=response.status, detail=response.text())

            count += 1

        return JSONResponse(
            content={
                "status": "success",
                "detail": f"{count} messages successfully written",
            }
        )

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Exception: {e}\nTraceback: {error_trace}")
        return JSONResponse(
            content={"detail": "Internal Error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
