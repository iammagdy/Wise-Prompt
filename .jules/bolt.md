## 2024-02-14 - MagicMock Overhead in Performance Testing
**Learning:** `unittest.mock.MagicMock` introduces significant overhead (up to 0.5ms per call) which can obscure algorithmic improvements (e.g. O(N) vs O(1)) when benchmarking tight loops with large iteration counts (e.g. 40,000+).
**Action:** Use custom lightweight mock classes instead of `MagicMock` when performance benchmarking high-throughput loops.
