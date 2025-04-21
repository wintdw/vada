import asyncio
import json
import logging
from pathlib import Path

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from ..handler.customer import (
    get_manager_accounts,
    get_non_manager_accounts,
    get_all_accounts,
)
from ..model.google import GoogleAdsCredentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_credentials(config_path: str) -> GoogleAdsClient:
    """Load Google Ads client from config file"""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        credentials = GoogleAdsCredentials(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
            developer_token=config.get("developer_token"),
        )

        client_config = {
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "developer_token": credentials.developer_token,
            "refresh_token": credentials.refresh_token,
            "use_proto_plus": True,
        }

        return GoogleAdsClient.load_from_dict(client_config)

    except Exception as e:
        logger.error(f"Failed to load credentials: {str(e)}")
        raise


async def main():
    # Load credentials from config file
    config_path = Path(__file__).parent.parent / "google_ads.json"
    ga_client = await load_credentials(str(config_path))

    try:
        # Test get_manager_accounts
        logger.info("Fetching manager accounts...")
        manager_accounts = await get_manager_accounts(ga_client)
        logger.info(f"Found {len(manager_accounts)} manager accounts")
        for account in manager_accounts:
            logger.info(f"Manager: {account['name']} (ID: {account['customer_id']})")
            logger.info(f"Child accounts: {account['child_accounts_count']}")

        # Test get_non_manager_accounts
        logger.info("\nFetching non-manager accounts...")
        client_accounts = await get_non_manager_accounts(ga_client)
        logger.info(f"Found {len(client_accounts)} client accounts")
        for account in client_accounts:
            logger.info(
                f"Client: {account['name']} (ID: {account['customer_id']})"
                f" - Clicks: {account['metrics']['clicks']}"
                f" - Cost: {account['metrics']['cost']:.2f}"
            )

        # Test get_all_accounts
        logger.info("\nFetching all accounts...")
        all_accounts = await get_all_accounts(ga_client)
        logger.info(
            f"Total accounts: {all_accounts['total_accounts']}"
            f" (Managers: {len(all_accounts['manager_accounts'])},"
            f" Clients: {len(all_accounts['client_accounts'])})"
        )

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
