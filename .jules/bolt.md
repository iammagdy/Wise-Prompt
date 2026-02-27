## Performance Journal - Bolt ⚡

This journal tracks critical performance learnings, bottlenecks, and optimization results.

## 2024-05-23 - [Initial Setup]
**Learning:** Establishing a baseline for performance tracking.
**Action:** Always measure before and after optimizations.

## 2024-05-23 - [Crawler Queue Optimization]
**Learning:** In BFS web crawling, using `list` for the queue and `if url not in queue` (O(N)) inside the loop causes quadratic complexity. With 500 pages, this spiked execution to ~140s.
**Action:** Always use `collections.deque` for queues and a separate `set` for O(1) membership checks. Reduced time to ~13s.
