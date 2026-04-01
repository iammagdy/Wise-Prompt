## 2024-05-24 - [Title]
**Learning:** In crawler benchmarks with heavy queue load, O(N) list containment and pop operations cause significant execution time spikes (e.g., ~25s to 135s).
**Action:** Switch to `collections.deque` and an auxiliary `set` for lookups to reduce this to milliseconds.
