## 2026-01-26 - Connection Pooling in Web Crawlers
**Learning:** Using `requests.Session()` instead of one-off `requests.get()` calls in a loop provides a significant performance boost (measured ~26% improvement on localhost) by reusing TCP connections.
**Action:** Always use a session context manager when making multiple requests to the same host/domain.
