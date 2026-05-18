## 2024-05-30 - [Web Crawler Optimization]
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes.
**Action:** Switching to `collections.deque` and an auxiliary `set` for lookups reduces this to milliseconds.
