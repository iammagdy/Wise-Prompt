## 2024-05-20 - [O(N^2) Queue Blowup in BFS]
**Learning:** Python lists used as queues with `pop(0)` and explicit membership checking via `not in queue` create a massive O(N^2) performance bottleneck when iterating over hundreds of links per page.
**Action:** Always use `collections.deque` for queues and a supplementary `set` for O(1) containment checks in BFS web crawlers.
