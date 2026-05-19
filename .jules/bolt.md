## 2026-05-19 - [O(N) List Queue Overhead]
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes (e.g., ~80s to >100s). Also, performing expensive string parsing operations like urlparse(url).netloc before fast O(1) set membership checks measurably increases execution time.
**Action:** Always use collections.deque for O(1) pops and an auxiliary set for O(1) lookups in algorithmic queue processing. Reorder conditions to perform fast O(1) checks before expensive ones.
