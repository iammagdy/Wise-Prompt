
## 2026-05-08 - [O(N) List Operations in URL Queue]
**Learning:** Using `queue.pop(0)` and `url not in queue` on a standard Python list becomes a massive bottleneck in the web crawler when processing pages with many links, causing O(N^2) behavior.
**Action:** Use `collections.deque` for `popleft()` and an auxiliary `queued_urls = set()` to achieve O(1) containment checks when building crawling queues.
