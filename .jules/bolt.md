## 2026-01-27 - [Network Benchmarking on Localhost]
**Learning:** Benchmarking connection pooling (requests.Session) on localhost shows negligible gains because TCP handshake time is minimal (~0ms).
**Action:** When optimizing network code, mock the network latency or accept that localhost benchmarks only verify functional correctness and CPU overhead, not RTT savings. Or use large request counts.
