from fastapi import FastAPI, Request # type: ignore
import json
import os

# Create the FastAPI app instance
app = FastAPI()

# Path to the file where we will write the request data
FILE_PATH = 'data.json'

@app.post("/capture/")
async def capture_json(request: Request):
    # Parse the incoming JSON request body
    json_data = await request.json()

    # Write the received JSON data to a file
    try:
        with open(FILE_PATH, 'a') as file:  # Open file in append mode
            file.write(json.dumps(json_data) + "\n")  # Write as a JSON string, followed by a newline
        return {"message": "Data captured successfully!"}
    except Exception as e:
        return {"error": str(e)}