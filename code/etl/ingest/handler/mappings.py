import asyncio
from typing import Dict

from libs.connectors.mappings import MappingsClient
from libs.utils.es_field_types import construct_es_mappings


# Create a global lock for setting mappings
set_mappings_lock = asyncio.Lock()


async def create_es_mappings(
    mappings_client: MappingsClient, index_name: str, field_types: Dict
) -> Dict:
    """Create Elasticsearch mappings using the mappings service

    Args:
        mappings_client: Client for interacting with mappings service
        index_name: Name of the index
        field_types: Dictionary of field types to create mappings from

    Returns:
        Dict containing the response from the mappings service
    """
    async with set_mappings_lock:
        mappings = construct_es_mappings(field_types)
        return await mappings_client.create_es_mappings(index_name, mappings)


async def copy_crm_mappings(
    mappings_client: MappingsClient,
    user_id: str,
    index_name: str,
    index_friendly_name: str = None,
) -> Dict:
    async with set_mappings_lock:
        return await mappings_client.copy_mappings(
            user_id, index_name, index_friendly_name
        )
