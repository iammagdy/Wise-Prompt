## 2024-05-24 - [Optimize recursive_crawl queue and condition checks]
**Learning:** Using lists for queueing and O(N) lookup operations (e.g., `pop(0)` and `in`) within web crawling loops causes significant overhead. Furthermore, executing string parsing (like `urlparse().netloc`) before fast O(1) set lookups creates unnecessary processing time.
**Action:** Always use `collections.deque` for queues and auxiliary `set`s for fast O(1) membership lookups. Place fast negative condition checks (e.g., `not in set`) before expensive parsing operations to short-circuit earlier.
