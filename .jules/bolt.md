## 2024-05-18 - [Web Crawler Optimizations]
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes (e.g., ~119s to 0.8s); additionally, expensive operations like `urlparse(url).netloc` should be done *after* fast O(1) set membership checks.
**Action:** Switch to `collections.deque` and an auxiliary `set` for lookups, and re-order condition checks to short-circuit on fast path.
