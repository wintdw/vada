import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from typing import Dict, Optional


class AsyncMongoProcessor:
    def __init__(self, mongo_uri: str):
        """
        Initialize AsyncMongoProcessor with MongoDB URI.
        """
        self.mongo_uri = mongo_uri
        self.client = None

    async def _create_client(self):
        """Create MongoDB client if not already created."""
        if self.client is None:
            try:
                self.client = AsyncIOMotorClient(self.mongo_uri)
                logging.info(f"Connected to MongoDB at {self.mongo_uri}")
            except PyMongoError as e:
                logging.error(f"Error connecting to MongoDB: {e}")
                raise  # Re-raise the exception to propagate it

    async def insert_document(
        self, db: str, coll: str, document: Dict
    ) -> Optional[str]:
        """
        Insert a document into the MongoDB collection.

        Returns the inserted document's _id as a string.
        """
        await self._create_client()

        try:
            result = await self.client[db][coll].insert_one(document)
            logging.info(f"Document inserted with _id: {result.inserted_id}")
            return str(result.inserted_id)  # Return inserted document's ID as string
        except PyMongoError as e:
            logging.error(f"Error inserting document into {db}.{coll}: {e}")
            return None

    async def find_document(self, db: str, coll: str, query: Dict) -> Optional[Dict]:
        """
        Find a single document based on the query.

        Returns the document if found, or None.
        """
        await self._create_client()

        try:
            document = await self.client[db][coll].find_one(query)
            if document:
                logging.info(f"Document found: {document}")
            else:
                logging.info(
                    f"No document found in {db}.{coll} matching query: {query}"
                )
            return document
        except PyMongoError as e:
            logging.error(f"Error finding document in {db}.{coll}: {e}")
            return None

    async def close_client(self):
        """
        Close MongoDB client connection gracefully.
        """
        if self.client:
            self.client.close()
            logging.info("MongoDB client connection closed.")
