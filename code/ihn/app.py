from fastapi import FastAPI, Request, HTTPException # type: ignore
import json
import os
from typing import Any, Dict

# Create the FastAPI app instance
app = FastAPI()

# Path to the directory where we will write the request data
DIR_PATH = '/app/data'

@app.post("/capture")
async def capture_json(request: Request) -> Dict[str, Any]:
    # Parse the incoming JSON request body
    json_data = await request.json()

    # Ensure the directory exists
    os.makedirs(DIR_PATH, exist_ok=True)

    # Extract the table_fullname from the JSON data
    table_fullname = json_data.get("table_fullname")
    if not table_fullname:
        raise HTTPException(status_code=400, detail="Missing 'table_fullname' in the request data")

    # Construct the file path based on table_fullname
    file_name = f"{table_fullname.replace('.', '_')}.json"
    file_path = os.path.join(DIR_PATH, file_name)

    # Write the received JSON data to the specified file
    try:
        with open(file_path, 'a') as file:  # Open file in append mode
            json.dump(json_data, file)  # Write as a JSON string
            file.write("\n")  # Add a newline for each entry
        return {"message": "Data captured successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))