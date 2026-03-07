## 2024-05-24 - Web Crawler Queue Performance Spike
**Learning:** Using a list for the `queue` in `recursive_crawl` with `queue.pop(0)` and `full_url not in queue` causes O(N) operations on every loop iteration. In crawler benchmarks with heavy queue load, these operations cause significant execution time spikes (e.g., ~4.5s for 20k items).
**Action:** Use `collections.deque` for O(1) pops and maintain an auxiliary `queued_urls` set for O(1) lookups to reduce queue operations to milliseconds.
