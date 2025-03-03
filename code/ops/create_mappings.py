import sys
import os
import click
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libs.connectors.mappings import MappingsClient


@click.command()
@click.argument("base_url")
@click.argument("user_id")
@click.argument("index_name")
@click.option("--index_friendly_name", default="", help="Friendly name for the index")
@click.option("--id_field", default="", help="ID field for the mappings")
@click.option("--agg_field", default="", help="Aggregation field for the mappings")
@click.option("--time_field", default="", help="Time field for the mappings")
def create_mappings(
    base_url, user_id, index_name, index_friendly_name, id_field, agg_field, time_field
):
    async def main():
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

    asyncio.run(main())


if __name__ == "__main__":
    create_mappings()
