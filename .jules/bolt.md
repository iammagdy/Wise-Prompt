## 2024-05-23 - Crawler Queue Performance
**Learning:** Checking `item not in list` for deduplication in a crawler queue creates an O(N^2) bottleneck. In `recursive_crawl`, this caused massive slowdowns as the queue grew.
**Action:** Always use a separate `set` (O(1)) for membership checks alongside `collections.deque` (O(1) pop) for queues.
