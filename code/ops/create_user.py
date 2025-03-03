import sys
import os
import click
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libs.connectors.mappings import MappingsClient


@click.command()
@click.argument("base_url")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_user(base_url, username, email, password):
    async def main():
        try:
            client = MappingsClient(base_url)
            await client.create_user(username, email, password)
            print(f"User {username} created successfully")
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            sys.exit(1)

    asyncio.run(main())


if __name__ == "__main__":
    create_user()
