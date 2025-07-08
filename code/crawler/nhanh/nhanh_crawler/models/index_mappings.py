import json
import os

# Define the path to the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), "index_mappings.json")

index_mappings_data = {}
# Load the JSON data
with open(json_file_path, "r") as file:
    index_mappings_data = json.load(file)
