## 2024-05-24 - O(N) List Queue Bottleneck in Crawler
**Learning:** Using `queue.pop(0)` and `url not in queue` on a Python list for large crawl queues causes severe O(N) performance degradation under load (e.g. processing pages with many links). Also, fast-path checks (like checking `visited` and `queued_urls` sets) should precede expensive string-parsing calls like `urlparse`.
**Action:** Use `collections.deque` with `popleft()` and an auxiliary set (`queued_urls`) for O(1) containment checks. Order conditional checks so fast O(1) checks run first.
