## 2025-02-20 - Web Crawler Queue Algorithmic Bottleneck
**Learning:** Using `queue.pop(0)` and `not in queue` list traversal with `urlparse` inside a nested loop causes O(N) and high string-parsing overhead, resulting in massive execution time spikes under load.
**Action:** Use `collections.deque` for O(1) pops, an auxiliary `set` for O(1) containment checks, and short-circuit fast condition checks before expensive string operations like `urlparse`.
