## 2024-05-22 - [Connection Pooling in Crawler]
**Learning:** `requests.get` creates a new connection for every call. In a loop, this adds significant overhead due to SSL handshakes.
**Action:** Always use `requests.Session()` for repeated requests to the same host or in loops.
