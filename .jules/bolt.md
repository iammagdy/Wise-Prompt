## 2026-02-21 - List vs Deque Performance
**Learning:** Using a Python `list` as a queue (`pop(0)`) scales poorly ($O(N)$) and containment checks (`in list`) are also $O(N)$. Combining these inside a loop resulted in $O(N^2)$ complexity for `recursive_crawl`, significantly slowing down web scanning as the queue grew.
**Action:** Always use `collections.deque` for FIFO queues (`popleft()` is $O(1)$) and maintain a separate `set` for containment checks ($O(1)$) to ensure scalable performance in queue-based algorithms.
