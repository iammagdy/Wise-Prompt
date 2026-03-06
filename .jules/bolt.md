
## 2024-03-24 - recursive_crawl Queue Bottleneck
**Learning:** In web crawler implementations processing heavy queue loads with many links, checking for `if full_url not in queue` and doing `queue.pop(0)` where `queue` is a standard list becomes an O(N) operation and causes execution time spikes (~18 seconds for processing 3 pages with 20000 links).
**Action:** Always use `collections.deque` paired with an auxiliary set for O(1) containment checks when managing queues in BFS/scraping algorithms.
