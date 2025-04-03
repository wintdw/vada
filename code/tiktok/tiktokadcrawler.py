import aiohttp
import json
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
        headers: Dict[str, str] = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

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

    async def get_advertiser_info(self, advertiser_id: str) -> Dict:
        """
        Method to fetch detailed advertiser information.

        Args:
            advertiser_id (str): The ID of the advertiser to fetch information for.

        Returns:
            dict: A dictionary containing advertiser information including:
                - advertiser_id: The unique identifier for the advertiser
                - name: Name of the advertiser
                - company: Company name
                - status: Account status (e.g., "STATUS_ENABLE")
                - currency: Currency used for the account
                - timezone: Timezone setting
                - balance: Account balance
                - address: Company address
                - country: Country code
                - industry: Industry code
                - email: Contact email (partially masked)
                - telephone_number: Contact phone (partially masked)
                - role: Advertiser role (e.g., "ROLE_CHILD_ADVERTISER")
                And other advertiser-specific fields

        Example response:
            {
                "advertiser_id": "7447426955642961937",
                "name": "AF-TT-NS015-10APL2502-GMT-2",
                "company": "ANCHI GROUP VIET NAM JOINT STOCK",
                "status": "STATUS_ENABLE",
                "balance": 2390120.0,
                "currency": "VND"
            }
        """
        endpoint: str = "/advertiser/info/"
        params: Dict[str, str] = {"advertiser_ids": json.dumps([advertiser_id])}

        response: Dict = await self._get(endpoint, params)

        if (
            "data" in response
            and "list" in response["data"]
            and response["data"]["list"]
        ):
            return response["data"]["list"][0]
        return {}

    async def get_advertiser(self) -> List[Dict[str, str]]:
        """
        Method to fetch all advertisers in the account.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing advertiser information:
                - advertiser_id: The unique identifier for the advertiser
                - advertiser_name: Name of the advertiser

        Example response:
            [
                {
                    "advertiser_id": "7205119211688017922",
                    "advertiser_name": "ANCHITEX 01 +7"
                },
                {
                    "advertiser_id": "7211736173327253506",
                    "advertiser_name": "02-HIEU +7"
                }
            ]
        """
        endpoint: str = "/oauth2/advertiser/get/"
        params: Dict[str, str] = {"app_id": self.app_id, "secret": self.secret}

        response: Dict = await self._get(endpoint, params)

        if "data" in response and "list" in response["data"]:
            return response["data"]["list"]
        return []

    async def get_ad(
        self,
        advertiser_id: str,
        campaign_ids: Optional[List[str]] = None,
        adgroup_ids: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Method to fetch all ad information, including pagination.

        Args:
            advertiser_id (str): The ID of the advertiser
            campaign_ids (List[str], optional): List of campaign IDs to filter ads. Defaults to None
            adgroup_ids (List[str], optional): List of ad group IDs to filter ads. Defaults to None

        Returns:
            list: A list of dictionaries, where each dictionary contains ad information including:
                - ad_id: The unique identifier for the ad
                - ad_name: Name of the ad
                - campaign_id: ID of the parent campaign
                - campaign_name: Name of the parent campaign
                - adgroup_id: ID of the parent ad group
                - adgroup_name: Name of the parent ad group
                - operation_status: Ad status (e.g., "ENABLE", "DISABLE")
                - creative_type: Type of creative
                - ad_format: Format of the ad (e.g., "SINGLE_VIDEO", "CATALOG_CAROUSEL")
                - landing_page_url: URL of the landing page
                - video_id: ID of the video if applicable
                - image_ids: List of image IDs
                And other ad-specific fields
        """
        endpoint: str = "/ad/get/"
        all_ads: List[Dict] = []
        page: int = 1

        while True:
            params: Dict[str, str] = {
                "advertiser_id": advertiser_id,
                "page": str(page),
                "page_size": "100",  # Using larger page size for efficiency
            }

            if campaign_ids:
                params["campaign_ids"] = json.dumps(campaign_ids)

            if adgroup_ids:
                params["adgroup_ids"] = json.dumps(adgroup_ids)

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

    async def get_adgroup(
        self, advertiser_id: str, campaign_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Method to fetch all ad group information, including pagination.

        Args:
            advertiser_id (str): The ID of the advertiser
            campaign_ids (List[str], optional): List of campaign IDs to filter ad groups. Defaults to None.

        Returns:
            list: A list of dictionaries, where each dictionary contains ad group information including:
                - adgroup_id: The unique identifier for the ad group
                - adgroup_name: Name of the ad group
                - campaign_id: ID of the parent campaign
                - campaign_name: Name of the parent campaign
                - operation_status: Ad group status (e.g., "ENABLE", "DISABLE")
                - budget: Ad group budget amount
                - budget_mode: Budget mode setting
                - placement_type: Type of placement
                - optimization_goal: Optimization goal setting
                - billing_event: Billing event type
                And other ad group-specific fields
        """
        endpoint: str = "/adgroup/get/"
        all_adgroups: List[Dict] = []
        page: int = 1

        while True:
            params: Dict[str, str] = {
                "advertiser_id": advertiser_id,
                "page": str(page),
                "page_size": "100",  # Using larger page size for efficiency
            }

            if campaign_ids:
                params["campaign_ids"] = json.dumps(campaign_ids)

            adgroup_info: Dict = await self._get(endpoint, params)
            if "data" in adgroup_info and "list" in adgroup_info["data"]:
                all_adgroups.extend(adgroup_info["data"]["list"])
                page_info: Dict = adgroup_info["data"].get("page_info", {})
                total_pages: int = page_info.get("total_page", 0)
                if page >= total_pages:
                    break
                page += 1
            else:
                break

        return all_adgroups

    async def get_campaign(self, advertiser_id: str) -> List[Dict]:
        """
        Method to fetch all campaign information, including pagination.

        Args:
            advertiser_id (str): The ID of the advertiser.

        Returns:
            list: A list of dictionaries, where each dictionary contains campaign information including:
                - campaign_id: The unique identifier for the campaign
                - campaign_name: Name of the campaign
                - campaign_type: Type of campaign (e.g., "REGULAR_CAMPAIGN")
                - objective: Campaign objective (e.g., "LANDING_PAGE")
                - objective_type: Type of objective (e.g., "LEAD_GENERATION")
                - budget: Campaign budget amount
                - budget_mode: Budget mode setting
                - operation_status: Campaign status (e.g., "ENABLE", "DISABLE")
                - create_time: Campaign creation timestamp
                - modify_time: Last modification timestamp
                And other campaign-specific fields
        """
        endpoint: str = "/campaign/get/"
        all_campaigns: List[Dict] = []
        page: int = 1

        while True:
            params: Dict[str, str] = {
                "advertiser_id": advertiser_id,
                "page": str(page),
                "page_size": "100",  # Using larger page size for efficiency
            }
            campaign_info: Dict = await self._get(endpoint, params)
            if "data" in campaign_info and "list" in campaign_info["data"]:
                all_campaigns.extend(campaign_info["data"]["list"])
                page_info: Dict = campaign_info["data"].get("page_info", {})
                total_pages: int = page_info.get("total_page", 0)
                if page >= total_pages:
                    break
                page += 1
            else:
                break

        return all_campaigns

    async def get_integrated_report(
        self,
        advertiser_id: str,
        start_date: str,
        end_date: str,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        report_type: str = "BASIC",
        data_level: str = "AUCTION_AD",
        enable_total_metrics: bool = True,
    ) -> List[Dict]:
        """
        Method to fetch integrated report data with pagination support.

        Args:
            advertiser_id (str): The ID of the advertiser
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            metrics (List[str], optional): List of metrics to fetch. Defaults to basic engagement metrics
            dimensions (List[str], optional): List of dimensions. Defaults to ["ad_id"]
            report_type (str, optional): Type of report. Defaults to "BASIC"
            data_level (str, optional): Level of data aggregation. Defaults to "AUCTION_AD"
            enable_total_metrics (bool, optional): Whether to include total metrics. Defaults to True

        Returns:
            List[Dict]: List of report data entries
        """
        endpoint: str = "/report/integrated/get/"
        all_reports: List[Dict] = []
        page: int = 1

        if dimensions is None:
            dimensions = ["ad_id", "stat_time_day"]

        if metrics is None:
            metrics = [
                "spend",
                "billed_cost",
                "cash_spend",
                "voucher_spend",
                "cpc",
                "cpm",
                "impressions",
                "gross_impressions",
                "clicks",
                "ctr",
                "reach",
                "cost_per_1000_reached",
                "frequency",
                "conversion",
                "cost_per_conversion",
                "conversion_rate",
                "conversion_rate_v2",
                "real_time_conversion",
                "real_time_cost_per_conversion",
                "real_time_conversion_rate",
                "real_time_conversion_rate_v2",
                "result",
                "cost_per_result",
                "result_rate",
                "real_time_result",
                "real_time_cost_per_result",
                "real_time_result_rate",
                "secondary_goal_result",
                "cost_per_secondary_goal_result",
                "secondary_goal_result_rate",
            ]

        while True:
            params: Dict[str, str] = {
                "advertiser_id": advertiser_id,
                "report_type": report_type,
                "dimensions": json.dumps(dimensions),
                "data_level": data_level,
                "start_date": start_date,
                "end_date": end_date,
                "enable_total_metrics": str(enable_total_metrics).lower(),
                "metrics": json.dumps(metrics),
                "page": str(page),
                "page_size": "100",  # Using larger page size for efficiency
            }

            report_data: Dict = await self._get(endpoint, params)

            if "data" in report_data and "list" in report_data["data"]:
                all_reports.extend(report_data["data"]["list"])
                page_info: Dict = report_data["data"].get("page_info", {})
                total_pages: int = page_info.get("total_page", 0)

                if page >= total_pages:
                    break
                page += 1
            else:
                break

        return all_reports
