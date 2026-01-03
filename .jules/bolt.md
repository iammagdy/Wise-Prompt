## 2024-05-23 - [Requests Session & List Accumulation]
**Learning:** `requests.get` creates a new connection for every call. In a crawler loop, this adds significant overhead (DNS + TCP handshake + SSL) for every page. Using `requests.Session()` reuses the connection.
**Action:** Always use `requests.Session()` when making multiple requests to the same host/domain. Also, prefer list `append` + `join` over `+=` for string concatenation in loops.
