## 2024-05-24 - [O(1) Data Structures for Crawler Queues]
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment (`if url not in queue`) and pop operations (`queue.pop(0)`) cause significant execution time spikes.
**Action:** Switch to `collections.deque` for O(1) pops and use an auxiliary `set` for O(1) queue containment checks.

## 2024-05-24 - [Short-Circuit Expensive Operations]
**Learning:** In Python loops handling URLs, such as `recursive_crawl`, performing expensive string parsing operations like `urlparse(url).netloc == base_domain` before fast O(1) set membership checks (`url not in visited`) results in wasted computation and measurable performance drops.
**Action:** Order condition checks to perform fast O(1) lookups before executing slow parsing operations.