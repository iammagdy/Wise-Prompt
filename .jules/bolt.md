## 2024-05-23 - Crawler Optimization
**Learning:** `recursive_crawl` used inefficient string concatenation in a loop ($O(n^2)$) and list-based queue `pop(0)` ($O(n)$).
**Action:** Replaced with list accumulation + `join()` ($O(n)$) and `collections.deque` ($O(1)$ popleft). Also added `requests.Session` for connection pooling.
