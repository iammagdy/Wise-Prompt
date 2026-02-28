## 2024-02-28 - Replace O(N) list operations with O(1) in web crawler queue
**Learning:** O(N) list containment checks (`url not in list`) and `pop(0)` can cause execution time to spike quadratically ($O(N^2)$) during web crawling as the queue grows, causing massive performance degradation for large scans.
**Action:** Replace `list` queues with `collections.deque` for $O(1)$ pops from the left, and use an additional `set` to track queued items for $O(1)$ containment lookups.
