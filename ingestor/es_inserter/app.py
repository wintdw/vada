import json
import hashlib
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests

app = FastAPI()

ELASTICSEARCH_URL = "http://demo.internal.vadata.vn:9200"
ELASTIC_PASSWORD = "your_password_here"  # Set your password securely

class Event(BaseModel):
    index_name: str = Field(..., description="Index name must be present")
    message: str
    # Add additional fields as necessary

@app.post("/logs")
async def receive_logs(request: Request):
    try:
        # Parse the incoming JSON
        event_data = await request.json()
        event = Event(**event_data)

        # Check for required index_name
        if not event.index_name:
            raise HTTPException(status_code=400, detail="Missing index_name field")

        # Concatenate specified fields
        concatenated_fields = ""
        for key, value in event.dict().items():
            if key.startswith("@") or key in {"tags", "host", "port", "ip_address"}:
                continue
            concatenated_fields += str(value)

        # Create a SHA256 fingerprint
        fingerprint = hashlib.sha256(concatenated_fields.encode()).hexdigest()

        # Prepare data for Elasticsearch
        doc = event.dict()
        doc["concat_fields"] = concatenated_fields
        doc["fingerprint"] = fingerprint

        # Send to Elasticsearch
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{event.index_name}/_doc/{fingerprint}",
            json=doc,
            auth=("elastic", ELASTIC_PASSWORD)
        )

        # Check response from Elasticsearch
        if response.status_code not in {200, 201}:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        return JSONResponse(content={"status": "success", "fingerprint": fingerprint})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# To run the FastAPI app, use: uvicorn filename:app --host 0.0.0.0 --port 9801
