## 2023-10-25 - [Optimize URL crawling]
**Learning:** Using O(n) array lookups (`full_url not in queue`) and popping from the front of arrays (`queue.pop(0)`) is extremely slow for a large number of queued items.
**Action:** When queuing URLs in Python, use `collections.deque` for O(1) pops and use a parallel `set` (e.g. `queued_urls`) for O(1) contains checks before doing expensive string manipulation.
