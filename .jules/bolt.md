
## 2024-05-18 - Avoid fast-path string checks and urlparse overhead in inner loops
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes. Additionally, using `urlparse` on every link before checking O(1) set membership significantly degrades performance.
**Action:** Use `collections.deque` for O(1) pops and an auxiliary `set` for O(1) lookups. In loops, perform fast O(1) set membership checks (`url not in visited`) before executing expensive string parsing operations like `urlparse(url).netloc`.
