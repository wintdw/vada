import requests
import yaml
import time
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from jsonschema import validate, ValidationError
from threading import Lock

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


class APIMonitorService:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.route_groups = self.config["routes"]
        self.tokens = {}  # cache token per auth block
        self.lock = Lock()

    def _auth_key(self, auth_conf):
        return f"{auth_conf['url']}|{auth_conf.get('username', '')}"

    def get_access_token(self, auth_conf):
        """Authenticate with POST username/password or client credentials"""
        key = self._auth_key(auth_conf)
        with self.lock:
            if key in self.tokens:
                return self.tokens[key]

            if auth_conf.get("type") == "login":
                # login with username/password
                resp = requests.post(auth_conf["url"], json=auth_conf["payload"])
            else:
                # fallback: oauth client credentials
                resp = requests.post(auth_conf["url"], data={
                    "client_id": auth_conf["client_id"],
                    "client_secret": auth_conf["client_secret"],
                    "grant_type": "client_credentials"
                })

            resp.raise_for_status()
            token_field = auth_conf.get("token_field", "access_token")
            token = resp.json().get(token_field)
            if not token:
                raise ValueError(f"Token field '{token_field}' not found in response")
            self.tokens[key] = token
            return token

    def call_api(self, group_name, auth_conf, url, method="GET", headers=None, data=None, params=None):
        token = self.get_access_token(auth_conf)
        auth_headers = {"Authorization": f"Bearer {token}"}
        if headers:
            auth_headers.update(headers)

        start_time = time.time()
        resp = requests.request(method, url, headers=auth_headers, json=data, params=params)
        latency = time.time() - start_time

        api_latency.labels(group=group_name, route=url).set(latency)
        api_requests_total.labels(group=group_name, route=url, method=method).inc()

        if resp.status_code >= 400:
            api_requests_failed.labels(group=group_name, route=url, method=method).inc()

        return resp

    def validate_response(self, response_json, expected_schema, group_name, route):
        try:
            validate(instance=response_json, schema=expected_schema)
            api_response_valid.labels(group=group_name, route=route).inc()
            return True, None
        except ValidationError as e:
            api_response_invalid.labels(group=group_name, route=route).inc()
            return False, str(e)

    def run_check(self):
        results = []
        for group in self.route_groups:
            group_name = group.get("name", "unknown")
            auth_conf = group["auth"]
            for api in group["apis"]:
                try:
                    resp = self.call_api(group_name, auth_conf, api["url"], method=api.get("method", "GET"))
                    ok, err = self.validate_response(resp.json(), api["expected_schema"], group_name, api["url"])
                    results.append({
                        "group": group_name,
                        "url": api["url"],
                        "status": "ok" if ok else "failed",
                        "error": err
                    })
                except Exception as e:
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
