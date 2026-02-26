## 2025-02-23 - Crawler Queue Bottleneck
**Learning:** O(N) list containment checks (`url in queue`) inside the crawler loop caused massive slowdowns (133s) as the queue grew. Switching to `collections.deque` for O(1) pops and a separate `set` for O(1) containment checks reduced execution time to 16s (8x speedup).
**Action:** Always verify time complexity of queue operations in tight loops; use `set` for lookups alongside `deque` for ordering.
