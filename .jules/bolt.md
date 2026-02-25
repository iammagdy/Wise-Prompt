## 2025-02-23 - Queue Optimization Impact
**Learning:** Replacing list with deque in crawler showed minimal gains because the 'visited' set check short-circuits most queue lookups. The optimization only helps when checking unvisited URLs that are already in the queue (frontier collisions).
**Action:** When optimizing crawlers, focus on visited check efficiency first; queue optimization is secondary unless frontier is huge.
