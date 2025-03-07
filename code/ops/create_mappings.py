import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libs.connectors.mappings import MappingsClient


async def create_mappings(
    base_url,
    user_id,
    index_name,
    index_friendly_name="",
    id_field="",
    agg_field="",
    time_field="",
):
    try:
        client = MappingsClient(base_url)
        response = await client.create_mappings(
            user_id,
            index_name,
            index_friendly_name,
            id_field,
            agg_field,
            time_field,
        )
        print(f"Mappings created successfully: {response}")
    except Exception as e:
        print(f"Error creating mappings: {str(e)}")
        sys.exit(1)


# Example usage
if __name__ == "__main__":
    base_url = "http://mappings-dev.internal.vadata.vn"
    user_id = "123456"
    index_name = "index_name"
    index_friendly_name = "friendly_name"
    id_field = "id"
    agg_field = "agg"
    time_field = "time"

    asyncio.run(
        create_mappings(
            base_url,
            user_id,
            index_name,
            index_friendly_name,
            id_field,
            agg_field,
            time_field,
        )
    )
