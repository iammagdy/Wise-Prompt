## 2024-05-24 - [Optimize Crawler Queue]
**Learning:** Using a list as a queue (`pop(0)`) and for containment checks (`url in queue`) scales poorly (O(N)) under load. Also, doing string parsing (`urlparse`) before fast containment checks introduces unnecessary overhead.
**Action:** Use `collections.deque` for O(1) pops and an auxiliary `set` for O(1) queue containment checks. Perform O(1) set checks before expensive string operations like `urlparse`.
