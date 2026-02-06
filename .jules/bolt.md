## 2025-02-20 - [List vs Deque in Crawlers]
**Learning:** Using `queue.pop(0)` and `item in queue` (list) inside a crawler loop created an O(N^2) bottleneck that was 8x slower than using `deque` and a separate `set` for lookups on large crawls.
**Action:** Always use `collections.deque` for queues and `set` for membership checks in iteration loops.
