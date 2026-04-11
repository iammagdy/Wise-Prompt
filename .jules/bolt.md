
## 2024-04-11 - [O(n) list lookups block event loop in high-volume queues]
**Learning:** Checking `full_url not in queue` where `queue` is a standard Python `list` results in an O(n) operation per link found. On pages with thousands of links or when crawling many pages, this scaling becomes a bottleneck. Furthermore, `urlparse` is a relatively expensive parsing operation, doing this before doing fast set inclusion checks performs much worse.
**Action:** Always maintain a parallel `set()` of queued items (e.g. `queued_urls`) for O(1) existence checks alongside `collections.deque` for O(1) pops, and perform set containment checks BEFORE doing expensive string/URL parsing.
