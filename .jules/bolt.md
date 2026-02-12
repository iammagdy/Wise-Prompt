## 2026-02-12 - [Recursive Crawl Optimization]
**Learning:** Found O(N) queue operations (`pop(0)`) and O(N^2) string concatenation (`+=`) in `recursive_crawl`. While benchmarks on mock data showed ~15% improvement, the algorithmic complexity reduction from O(N^2) to O(N) is critical for scalability on large crawls.
**Action:** Always prefer `collections.deque` for queues and list join for string accumulation in loop-heavy operations.
