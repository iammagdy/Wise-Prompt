## 2026-01-21 - Requests Session Optimization
**Learning:** Initializing `requests.Session()` reuses the underlying TCP connection (Keep-Alive), which significantly reduces latency for crawlers making multiple requests to the same domain.
**Action:** Always use `requests.Session()` when making multiple requests to the same host in a loop.

## 2026-01-21 - Artifact Management
**Learning:** Creating temporary benchmark files (`benchmark.py`) and directories (`dummy_site`) in the root without cleaning them up pollutes the repository and makes PR reviews harder.
**Action:** Always clean up temporary test files or place them in a dedicated `tests/` directory ignored by git if they are meant to persist.
