## 2026-02-17 - Queue Optimization in Crawlers
**Learning:** Python `list.pop(0)` and `item in list` are O(N) operations. In recursive crawling with thousands of URLs, this creates an O(N^2) bottleneck that can dominate execution time even with network latency.
**Action:** Always use `collections.deque` for queues and `set` for membership checks in crawling loops.
