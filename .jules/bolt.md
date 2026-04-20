
## 2024-05-18 - [Web Crawler Queue Optimization]
**Learning:** Using Python lists for queue operations (e.g., `queue.pop(0)` and `item not in queue`) creates severe O(N) performance bottlenecks during web crawling, especially under heavy iteration load. String operations like `urlparse` are relatively slow and dominate loop execution time when not properly short-circuited by faster set-membership checks.
**Action:** Always use `collections.deque` for queues to achieve O(1) pops, maintain an auxiliary `set` for O(1) containment checks instead of checking the queue directly, and ensure O(1) fast-path checks execute before expensive string parsing logic in conditional statements.
