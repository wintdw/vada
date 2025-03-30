import aiohttp
import asyncio
import json
import hashlib
from typing import Optional, Dict, List


class TiktokAdCrawler:
    def __init__(self, access_token: str, app_id: str, secret: str) -> None:
        self.access_token: str = access_token
        self.app_id: str = app_id
        self.secret: str = secret
        self.base_url: str = "https://business-api.tiktok.com/open_api/v1.3"
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def _get(
        self, endpoint: str, params: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Helper method to perform GET requests.

        Args:
            endpoint (str): The API endpoint to append to the base URL.
            params (dict, optional): Query parameters to include in the request. Defaults to None.

        Returns:
            dict: The JSON response from the API, parsed into a Python dictionary.

        Raises:
            aiohttp.ClientResponseError: If the response status is not 200, with details about the failure.
        """
        url: str = self.base_url + endpoint
        headers: Dict[str, str] = {"Access-Token": self.access_token}

        if params is None:
            params = {}

        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_message: str = await response.text()
                raise aiohttp.ClientResponseError(
                    status=response.status,
                    message=f"Request failed with status {response.status}: {error_message}",
                )

    async def get_advertisers(self) -> Dict:
        """
        Method to fetch advertiser information.

        Returns:
            dict: A dictionary containing advertiser information.
        """
        endpoint: str = "/oauth2/advertiser/get/"
        params: Dict[str, str] = {"app_id": self.app_id, "secret": self.secret}

        advertisers: Dict = await self._get(endpoint, params)
        return advertisers

    async def get_ad(self, advertiser_id: str) -> List[Dict]:
        """
        Method to fetch all ad information, including pagination.

        Args:
            advertiser_id (str): The ID of the advertiser.

        Returns:
            list: A list of dictionaries, where each dictionary contains ad information.
        """
        endpoint: str = "/ad/get/"
        all_ads: List[Dict] = []
        page: int = 1

        while True:
            params: Dict[str, str] = {
                "advertiser_id": advertiser_id,
                "page": str(page),
                "page_size": "10",  # Adjust the page_size as needed
            }
            ad_info: Dict = await self._get(endpoint, params)
            if "data" in ad_info and "list" in ad_info["data"]:
                all_ads.extend(ad_info["data"]["list"])
                page_info: Dict = ad_info["data"].get("page_info", {})
                total_pages: int = page_info.get("total_page", 0)
                if page >= total_pages:
                    break
                page += 1
            else:
                break

        return all_ads


def generate_docid(doc: Dict) -> str:
    """
    Generates a unique document ID based on the serialized dictionary.

    Args:
        doc (Dict): The dictionary to generate the ID for.

    Returns:
        str: The generated document ID.
    """
    serialized_data = json.dumps(doc, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def append_metadata(data: List[Dict], metadata: Dict) -> List[Dict]:
    """
    Appends metadata to each dictionary in the list and generates a unique doc_id for each record.

    Args:
        data (List[Dict]): The list of dictionaries to process.
        metadata (Dict): The metadata to append to each dictionary.

    Returns:
        List[Dict]: The updated list of dictionaries with metadata and unique doc_id.
    """
    updated_data = []
    for record in data:
        # Merge the record with the metadata
        record_with_metadata = {**record, "_vada": metadata}
        updated_data.append(record_with_metadata)
    return updated_data


def write_to_jsonl(file_path: str, data: List[Dict], append: bool = False) -> None:
    """
    Writes a list of dictionaries to a JSONL file.

    Args:
        file_path (str): The path to the JSONL file.
        data (List[Dict]): The list of dictionaries to write.
        append (bool): If True, append to file; if False, overwrite. Default is False.
    """
    mode = "a" if append else "w"
    with open(file_path, mode) as file:
        for record in data:
            file.write(json.dumps(record, sort_keys=True) + "\n")


# Example usage
async def main():
    access_token = "xxx"
    app_id = "xxx"
    secret = "xxx"

    jsonl_file = "tiktok_ads.jsonl"

    metadata = {
        "ingest": {
            "source": "crawling:tiktok_ad",
            "destination": {"type": "elasticsearch", "index": "tiktok_ad"},
            "vada_client_id": "dw",
            "type": "tiktok_ad",
        }
    }

    tiktok_crawler: TiktokAdCrawler = TiktokAdCrawler(access_token, app_id, secret)

    try:
        advertisers: Dict = await tiktok_crawler.get_advertisers()
        if (
            advertisers
            and "data" in advertisers
            and "list" in advertisers["data"]
            and len(advertisers["data"]["list"]) > 0
        ):
            total_ads = 0
            # Write header to new file
            write_to_jsonl(jsonl_file, [])  # Create/clear the file

            # Iterate through all advertisers
            for advertiser in advertisers["data"]["list"]:
                advertiser_id: str = advertiser["advertiser_id"]
                print(f"Fetching ads for advertiser: {advertiser_id}")
                ads = await tiktok_crawler.get_ad(advertiser_id)

                if ads:
                    # Process and write ads for this advertiser immediately
                    updated_ads = append_metadata(ads, metadata)
                    write_to_jsonl(jsonl_file, updated_ads, append=True)
                    total_ads += len(ads)
                    print(f"Wrote {len(ads)} ads for advertiser {advertiser_id}")

            print(f"Ad information written to {jsonl_file}")
            print(f"Total ads collected: {total_ads}")
        else:
            print("No advertiser information found.")
    finally:
        await tiktok_crawler.session.close()


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
