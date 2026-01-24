## 2026-01-24 - Requests Session Optimization
**Learning:** `requests.Session()` provided a measurable ~5-10% speedup even on `localhost` where network latency is minimal. This confirms that connection pooling (TCP reuse) is impactful even without the heavy overhead of DNS/SSL/Latency of real internet traffic.
**Action:** Always prefer `requests.Session()` over one-off `requests.get()` inside loops, and verify with a local benchmark if possible.
