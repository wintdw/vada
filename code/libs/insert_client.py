import aiohttp  # type: ignore
from typing import List, Dict, Any, Optional
from pydantic import BaseModel  # type: ignore


class InsertRequest(BaseModel):
    meta: Dict[str, str]
    data: List[Dict[str, Any]]


class InsertClient:
    """Client for sending data to the insert service"""

    def __init__(self, base_url: str):
        """
        Initialize the insert client

        Args:
            base_url (str): Base URL of the insert service
        """
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Create aiohttp session when entering context"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context"""
        if self.session:
            await self.session.close()

    async def insert_json(
        self, index_name: str, documents: List[Dict[str, Any]]
    ) -> Dict:
        """
        Insert documents using the new /json endpoint

        Args:
            index_name (str): Name of the index to insert into
            documents (List[Dict]): List of documents to insert

        Returns:
            Dict: Response from the server

        Raises:
            RuntimeError: If client is not initialized
            aiohttp.ClientError: If request fails
        """
        if not self.session:
            raise RuntimeError("Client not initialized - use async with")

        request_data = InsertRequest(meta={"index_name": index_name}, data=documents)

        async with self.session.post(
            f"{self.base_url}/json", json=request_data.dict()
        ) as response:
            response_data = await response.json()
            if response.status >= 400:
                raise aiohttp.ClientError(f"Insert failed: {response_data}")

            return {"status": response.status, "detail": response_data}
