## 2024-05-23 - Performance Verification Paradox
**Learning:** Optimizing string concatenation ($O(N^2)$ to $O(N)$) showed no measurable gain in synthetic benchmarks because BeautifulSoup parsing dominated CPU time.
**Action:** When benchmarking CPU optimizations, isolate the specific operation or ensure the bottleneck isn't elsewhere (like heavy HTML parsing). However, the `requests.Session()` optimization remains valid for network latency (unmeasured by mocks).
