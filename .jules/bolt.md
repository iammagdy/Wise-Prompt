## 2025-02-18 - Crawler Queue Performance
**Learning:** Python list containment checks (`x in list`) are O(N), which becomes a significant bottleneck in breadth-first search queues when the queue grows large (e.g., >1000 items). Using a `set` for containment checks reduces this to O(1).
**Action:** Always pair a `queue` (deque) with a `visited` or `queued` set when implementing BFS or similar algorithms where duplicate checking is frequent.
