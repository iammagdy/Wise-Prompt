## 2024-05-23 - [Streamlit Session Optimization]
**Learning:** `requests.get` inside a loop creates a new connection for every request, which adds significant latency due to repeated TCP/SSL handshakes.
**Action:** Use `requests.Session()` (context manager) to reuse connections when making multiple requests, especially to the same domain.
