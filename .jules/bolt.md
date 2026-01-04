## 2024-05-23 - Session Reuse and String Concatenation
**Learning:** In a synchronous crawling loop, re-creating the `requests` connection for every URL adds significant overhead due to TCP handshakes. Also, string concatenation in a loop is $O(N^2)$ in Python.
**Action:** Always use `requests.Session()` for multiple requests to the same host, and use list accumulation + `.join()` for building large strings in loops.
