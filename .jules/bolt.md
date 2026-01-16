## 2025-02-23 - Session & List Optimization
**Learning:** In recursive crawling functions, `requests.get` inside a loop without a session causes full TCP handshake for every request.
**Action:** Always use `requests.Session()` (context manager) when making multiple requests to the same host/domain.
**Learning:** String concatenation `+=` in a loop scales quadratically.
**Action:** Prefer accumulating strings in a list and using `''.join(list)` at the end.
