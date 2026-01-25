## 2025-02-17 - Recursive Crawler Optimization
**Learning:** `requests.get` inside a loop creates a new TCP connection for every request, which is inefficient for crawling the same domain.
**Action:** Use `requests.Session()` to reuse connections (Keep-Alive) and reduce handshake overhead. Also, use list accumulation + `join()` instead of string concatenation in loops for better memory performance.
