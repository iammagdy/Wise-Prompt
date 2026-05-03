## 2025-02-18 - Algorithmic bottlenecks in tight crawler loops
**Learning:** In crawler loops parsing thousands of links, O(N) list containment checks (`url not in queue`) and fast-path string checks cause huge execution spikes.
**Action:** Always use `collections.deque` for O(1) pops, maintain an auxiliary `set()` for queue containment, and evaluate O(1) set lookups *before* expensive URL string parsing.
