import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libs.connectors.mappings import MappingsClient


async def create_user(base_url, username, email, password):
    try:
        client = MappingsClient(base_url)
        await client.create_user(username, email, password)
        print(f"User {username} created successfully")
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        sys.exit(1)


# Example usage
if __name__ == "__main__":
    base_url = "http://mappings-dev.internal.vadata.vn"
    username = "user123"
    email = "user@"
    password = "password"

    asyncio.run(create_user(base_url, username, email, password))
