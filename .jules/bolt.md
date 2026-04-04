
## 2025-05-14 - [O(N) List operations in web crawler queue]
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes.
**Action:** Switching to `collections.deque` and an auxiliary `set` for lookups reduces queue processing time from seconds to milliseconds. In loops, perform fast O(1) set membership checks before executing expensive string parsing operations like `urlparse(url).netloc`.
