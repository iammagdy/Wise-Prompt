## 2026-02-08 - [Algorithmic vs Synthetic Benchmarks]
**Learning:** Synthetic benchmarks for queue operations in BFS can be misleading if the graph structure (e.g., linear) naturally keeps duplicates at the head of the list, masking the O(N) scan cost.
**Action:** Trust algorithmic complexity (O(1) set lookup vs O(N) list scan) over micro-benchmarks for structural correctness, especially when the pathological case (large queue scan) is a real risk in production.
