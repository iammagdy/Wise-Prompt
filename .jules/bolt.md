## 2024-05-18 - [Web Crawler Optimization]
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes (e.g., ~25s to 133s); switching to `collections.deque` and an auxiliary `set` for lookups reduces this to milliseconds.
**Action:** In Python loops handling URLs, such as `recursive_crawl`, perform fast O(1) set membership checks (e.g., `url not in visited`) before executing expensive string parsing operations like `urlparse(url).netloc` to measurably reduce execution time.
