## 2024-03-28 - Optimizing BFS Queue Lookups in Web Crawler
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes. Also, string parsing operations like `urlparse` inside a loop are expensive.
**Action:** Switched to `collections.deque` for O(1) pops and added an auxiliary `set` for O(1) queue containment checks. Also, performed fast O(1) set membership checks before executing expensive string parsing operations to measurably reduce execution time.
