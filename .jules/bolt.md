
## 2024-05-24 - Crawler Algorithmic Bottleneck
**Learning:** In high-throughput Python loops handling URLs, evaluating expensive string parsing operations like `urlparse(url).netloc` before O(1) set membership checks (`url not in visited`) causes significant performance degradation. Additionally, using O(N) list operations (`pop(0)` and `in list`) for large crawler queues scales poorly.
**Action:** Always use `collections.deque` for queues, maintain an auxiliary set for O(1) lookups, and order boolean conditions so fast O(1) checks evaluate first, leveraging Python's short-circuit evaluation.
