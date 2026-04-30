
## 2026-04-30 - [O(N) List Queue Bottleneck]
**Learning:** In crawler loops under heavy queue load, O(N) list containment and pop operations cause significant execution time spikes. Using MagicMocks inside benchmarking loops masks algorithmic performance.
**Action:** Use collections.deque for O(1) pops and an auxiliary set for O(1) queue containment lookups. Benchmark algorithmic logic with primitive types.
