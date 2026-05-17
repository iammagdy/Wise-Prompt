
## 2024-05-18 - [Web Crawler Optimization]
**Learning:** Python lists used as queues (`queue.pop(0)`) and for containment checks (`in queue`) in BFS crawler algorithms scale poorly (O(N) operations), causing significant bottlenecks on large scans.
**Action:** Always replace lists with `collections.deque` for O(1) queue operations, use a companion `set` for O(1) lookup, and order loop conditions to perform fast set checks before expensive string parsing (`urlparse`).
