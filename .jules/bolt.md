
## 2024-05-20 - [O(1) Data Structures in Recursion]
**Learning:** In recursive tree crawling functions like `recursive_crawl` processing hundreds of links per page, O(N) list operations `queue.pop(0)` and `full_url not in queue` cause severe execution time bloat. Additionally, invoking string parsing operations like `urlparse()` before performing simple O(1) set membership checks drastically increases time.
**Action:** Always prefer `collections.deque` and auxiliary `set` data structures for queues that handle significant workloads. Evaluate expensive string or parsing functions and try to place them after fast-path condition checks like `item in set`.
