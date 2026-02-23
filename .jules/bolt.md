## 2024-05-23 - [Crawler Queue Optimization]
**Learning:** O(N) containment checks (`url in queue`) caused timeouts (>400s) at 1000 pages, while switching to `set` lookups reduced time to ~5.8s, proving queue management effectively dominates execution time in large crawls.
**Action:** Always use `set` for containment checks in crawler queues, and `collections.deque` for O(1) pops.
