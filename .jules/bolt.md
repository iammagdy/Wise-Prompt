# Bolt's Journal

## 2025-02-27 - Initial Setup
**Learning:** This project tracks performance optimizations.
**Action:** Always document learnings here.

## 2025-02-27 - Connection Pooling in Web Crawler
**Learning:** In a recursive web crawler making sequential requests to the same domain, reusing the TCP connection via `requests.Session()` provided an ~8% performance improvement on localhost by avoiding repeated handshakes.
**Action:** Always prefer `requests.Session()` over one-off `requests.get()` when making multiple requests to the same host, especially in loops.
