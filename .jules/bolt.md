
## 2024-03-20 - Fast Path Evaluation in List Loop Contains Check
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment (`in list`) and pop (`pop(0)`) operations cause significant execution time spikes. Furthermore, evaluating `urlparse` before performing simple O(1) cache lookups (`in set`) slows down link processing tremendously.
**Action:** Always use `collections.deque` paired with an auxiliary `set` for queues where membership tests are necessary. In loops handling URLs, position fast O(1) set checks before string operations like `urlparse(url).netloc == domain`.
