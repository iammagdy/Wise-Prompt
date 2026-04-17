## 2026-04-17 - [Deque and Evaluation Order Speedup]
**Learning:** O(N) list containment and pop operations cause significant execution time spikes under load (e.g., crawler with 50,000 items). Evaluating expensive string processing operations like `urlparse(url).netloc` before O(1) set membership checks compounds the problem.
**Action:** Use `collections.deque` and an auxiliary `set` for lookup queues to reduce processing from seconds to milliseconds. In loops, perform fast O(1) checks before slow operations to optimize execution time.
