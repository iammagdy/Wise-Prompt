## 2026-02-03 - Crawler Optimization
**Learning:** `collections.deque` and `requests.Session` provide standard, robust performance improvements for crawling logic over lists and one-off requests.
**Action:** Always prefer `deque` for queues (O(1) pops) and `Session` for multiple requests to the same host/domain (connection pooling).
