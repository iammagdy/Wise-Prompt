## 2024-05-24 - [O(1) Queue Optimization]
**Learning:** In the web crawler, using O(N) list operations (`pop(0)` and `not in queue`) caused massive performance degradation as queue load increased, simulating heavy latency.
**Action:** Always prefer `collections.deque` with an auxiliary `set` for containment checks during BFS/Queue operations to maintain predictable O(1) performance profiles.

## 2024-05-24 - [Loop Conditional Ordering]
**Learning:** Inside iteration loops handling large volumes of items (like parsing all links on a page), placing computationally expensive string parsing operations (like `urlparse`) before simple set containment checks wastes significant CPU cycles.
**Action:** Order conditional statements to utilize Python's short-circuiting: perform fast O(1) lookups (`not in visited`) first before executing expensive string manipulation or parsing methods.
