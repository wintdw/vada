# Copilot Instructions for VADA Codebase

## Architecture Overview
- The codebase is organized by service domain under `vada/code/`, with each subfolder (e.g., `acl`, `crawler`, `etl`, `ihn`, `libs`, `mappings`, `ops`) representing a distinct microservice or shared library.
- Each crawler (e.g., `tiktok`, `nhanh`, `shopee`, etc.) is further split into its own directory, with clear separation between scheduler logic, handler modules, and configuration files.
- Data flows from scheduler modules (e.g., `scheduler/crawl.py`) to handler modules (e.g., `handler/persist.py`, `handler/metrics.py`), which interact with external APIs, databases, and Prometheus metrics.
- Prometheus metrics are a first-class concern: every data persistence operation should update success/failure counters in `handler/metrics.py`.

## Developer Workflows
- **Crawlers:** Each crawler's scheduler runs periodic jobs, using APScheduler (`AsyncIOScheduler`) and async functions. First-time crawls are chunked and run in the background to avoid blocking regular updates.
- **Metrics:** Use Prometheus `Counter` for accumulating success/failure of inserts, and `Gauge` for time-based or label-only metrics. Always increment counters, never set them directly.
- **Configuration:** Environment-specific settings are loaded from `model/setting.py` or `model/settings.py`.
- **Testing:** No global test runner is present; tests are typically script-based under `ops/` or per-service. Run scripts directly for manual validation.
- **Docker:** Each service has its own Dockerfile and Compose YAMLs. Build and run containers using the relevant compose file in the service directory.

## Project-Specific Patterns
- **First Crawl Pattern:** For new data sources, use a chunked approach (e.g., 30 days at a time) and call the daily crawl function for each chunk. Always run first crawls as background tasks to avoid blocking the scheduler.
- **Metrics Update:** After every persistence operation, update Prometheus metrics using the correct labels (`crawl_id`, `index_name`, `app_env`).
- **Async Scheduling:** Use `asyncio.create_task` for background jobs and avoid awaiting long-running tasks in the main scheduler loop.
- **Error Logging:** Log errors with context (e.g., crawl_id, account_name) for traceability. Use try/except in scheduled jobs to prevent silent failures.

## Integration Points
- **External APIs:** Handlers interact with external APIs (e.g., TikTok, Nhanh) using access tokens and time-based queries.
- **Prometheus:** Metrics are exposed via Prometheus client; update metrics in handler modules after each operation.
- **Database/Insert Service:** Data is sent to insert services in batches, with batch size determined by `get_optimal_batch_size` in `handler/persist.py`.

## Examples
- See `vada/code/crawler/tiktok/tiktok_shop_crawler/scheduler/order.py` for chunked first crawl and metrics update pattern.
- See `vada/code/crawler/nhanh/nhanh_crawler/scheduler/crawl.py` for daily and first crawl orchestration.
- See `handler/metrics.py` in each service for Prometheus metric definitions and usage.

## Conventions
- Use snake_case for Python files and functions.
- Place service-specific logic under its domain directory; shared utilities go in `libs/`.
- Always update metrics after persistence, and log errors with full context.

## Cross-Service Consistency
- All services of the same type (e.g., crawlers) must follow the same logic and patterns for scheduling, chunked first crawls, metrics updates, and error handling. When adding a new crawler, reuse the structure and workflow from existing crawlers to ensure maintainability and predictability.

---

If any section is unclear or missing important details, please provide feedback or specify which workflows or patterns need further documentation.
