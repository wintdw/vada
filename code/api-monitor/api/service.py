import requests
import yaml
import time
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from jsonschema import validate, ValidationError
from threading import Lock
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

# ---------------- Prometheus Metrics ---------------- #
api_requests_total = Counter(
    "api_requests_total", "Total API requests made", ["group", "route", "method"]
)
api_requests_failed = Counter(
    "api_requests_failed", "Total API requests failed", ["group", "route", "method"]
)
api_response_valid = Counter(
    "api_response_valid", "API responses passed validation", ["group", "route"]
)
api_response_invalid = Counter(
    "api_response_invalid", "API responses failed validation", ["group", "route"]
)
api_latency = Gauge(
    "api_response_latency_seconds", "API response latency in seconds", ["group", "route"]
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class APIMonitorService:
    def __init__(self, config_path="config.yaml"):
        logger.info("Initializing APIMonitorService with config path: %s", config_path)
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.route_groups = self.config["routes"]
        self.tokens = {}  # cache token per auth block
        self.lock = Lock()

    def _auth_key(self, auth_conf):
        return f"{auth_conf['url']}|{auth_conf.get('username', '')}"

    def get_access_token(self, auth_conf):
        logger.info("Fetching access token for auth configuration: %s", auth_conf)
        key = self._auth_key(auth_conf)
        with self.lock:
            if key in self.tokens:
                logger.info("Using cached token for key: %s", key)
                return self.tokens[key]

            if auth_conf.get("type") == "login":
                logger.info("Authenticating with username/password at URL: %s", auth_conf["url"])
                resp = requests.post(auth_conf["url"], json=auth_conf["payload"])
            else:
                logger.info("Authenticating with client credentials at URL: %s", auth_conf["url"])
                resp = requests.post(auth_conf["url"], data={
                    "client_id": auth_conf["client_id"],
                    "client_secret": auth_conf["client_secret"],
                    "grant_type": "client_credentials"
                })

            resp.raise_for_status()
            token_field = auth_conf.get("token_field", "access_token")
            token = resp.json().get(token_field)
            if not token:
                logger.error("Token field '%s' not found in response", token_field)
                raise ValueError(f"Token field '{token_field}' not found in response")
            self.tokens[key] = token
            logger.info("Token fetched and cached for key: %s", key)
            return token

    def call_api(self, group_name, auth_conf, url, method="GET", headers=None, data=None, params=None):
        logger.info("Calling API: %s with method: %s", url, method)
        token = self.get_access_token(auth_conf)
        auth_headers = {"Authorization": f"Bearer {token}"}
        if headers:
            auth_headers.update(headers)

        start_time = time.time()
        try:
            resp = requests.request(method, url, headers=auth_headers, json=data, params=params)
            latency = time.time() - start_time

            api_latency.labels(group=group_name, route=url).set(latency)
            api_requests_total.labels(group=group_name, route=url, method=method).inc()

            if resp.status_code >= 400:
                api_requests_failed.labels(group=group_name, route=url, method=method).inc()
                logger.warning("API call failed with status code: %s", resp.status_code)
            else:
                logger.info("API call succeeded with status code: %s", resp.status_code)

            return resp
        except Exception as e:
            logger.error("Error during API call: %s", str(e))
            raise

    def validate_response(self, response_json, expected_schema, group_name, route):
        logger.info("Validating response for route: %s", route)
        try:
            validate(instance=response_json, schema=expected_schema)
            api_response_valid.labels(group=group_name, route=route).inc()
            logger.info("Response validation passed for route: %s", route)
            return True, None
        except ValidationError as e:
            api_response_invalid.labels(group=group_name, route=route).inc()
            logger.warning("Response validation failed for route: %s, error: %s", route, str(e))
            return False, str(e)

    def run_check(self):
        logger.info("Running API checks")
        results = []
        for group in self.route_groups:
            group_name = group.get("name", "unknown")
            auth_conf = group["auth"]
            for api in group["apis"]:
                try:
                    logger.info("Checking API: %s in group: %s", api["url"], group_name)
                    resp = self.call_api(group_name, auth_conf, api["url"], method=api.get("method", "GET"))
                    ok, err = self.validate_response(resp.json(), api["expected_schema"], group_name, api["url"])
                    results.append({
                        "group": group_name,
                        "url": api["url"],
                        "status": "ok" if ok else "failed",
                        "error": err
                    })
                except Exception as e:
                    logger.error("Error during check for API: %s, error: %s", api["url"], str(e))
                    results.append({
                        "group": group_name,
                        "url": api["url"],
                        "status": "error",
                        "error": str(e)
                    })
        return results


# ---------------- FastAPI App ---------------- #
app = FastAPI(title="API Monitor Service")
service = APIMonitorService("config.yaml")


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/check")
def check():
    return service.run_check()


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# Initialize the scheduler
scheduler = AsyncIOScheduler()

# Schedule the /check endpoint to run every day
def scheduled_check():
    logger.info("Scheduled /check endpoint execution started")
    service.run_check()
    logger.info("Scheduled /check endpoint execution completed")

scheduler.add_job(scheduled_check, IntervalTrigger(days=1), id="daily_check")

# Start the scheduler
scheduler.start()
