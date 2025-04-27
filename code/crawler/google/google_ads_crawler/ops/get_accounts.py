import requests
import json
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_refresh_tokens() -> List[str]:
    """Get list of refresh tokens to test"""
    return ["token1", "token2"]


def get_test_cases() -> List[Dict]:
    """Get list of test cases with different parameters"""
    return [
        {"params": {"account_type": "manager"}, "desc": "Get manager accounts"},
        {"params": {"account_type": "client"}, "desc": "Get client accounts"},
    ]


async def test_customers_endpoint():
    """Test different combinations of the customers endpoint with multiple tokens"""

    base_url = "http://localhost:8146/google/accounts"
    headers = {"Content-Type": "application/json"}

    for token_index, refresh_token in enumerate(get_refresh_tokens(), 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing with refresh token #{token_index}")
        logger.info("=" * 50)

        credentials = {"refresh_token": refresh_token}

        for test_case in get_test_cases():
            try:
                logger.info(f"\nTesting: {test_case['desc']}")

                response = requests.get(
                    base_url,
                    headers=headers,
                    params=test_case["params"],
                    json=credentials,
                )

                response.raise_for_status()

                # Log success results
                logger.info(f"Status Code: {response.status_code}")
                logger.info("Response Summary:")

                data = response.json()
                if "total_accounts" in data:
                    logger.info(f"Total Accounts: {data['total_accounts']}")
                if "accounts" in data:
                    account_count = len(data["accounts"])
                    logger.info(f"Accounts Retrieved: {account_count}")

                # Save detailed response to file
                output_file = f"customer_response_token{token_index}_{test_case['params'].get('account_type', 'all')}.json"
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Full response saved to: {output_file}")

            except requests.RequestException as e:
                logger.error(f"Error with token #{token_index}: {str(e)}")
                if hasattr(e, "response") and e.response is not None:
                    logger.error(f"Error response: {e.response.text}")

            logger.info("-" * 50)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_customers_endpoint())
