## 2025-02-17 - Optimizing Queue Operations in Recursive Functions
**Learning:** Using `list.pop(0)` and `list` membership checks (`x in list`) for queue operations leads to O(N^2) complexity, which can become a bottleneck in recursive crawling with many items. Python's `deque` provides O(1) pops and `set` provides O(1) lookups.
**Action:** Always use `collections.deque` for queues and a parallel `set` for membership checks when implementing BFS or similar algorithms involving large collections.
