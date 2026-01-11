## 2024-05-23 - [Optimization] Connection Pooling in Crawler
**Learning:** Instantiating a new `requests.Session()` (or using `requests.get`) for every request in a loop prevents connection reuse (keep-alive), leading to unnecessary TLS handshakes and TCP connections.
**Action:** Always use a context manager `with requests.Session() as session:` when performing multiple requests to the same host or during a crawling operation. This allows the underlying `urllib3` to pool connections.
