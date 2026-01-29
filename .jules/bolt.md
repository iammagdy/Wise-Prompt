## 2026-01-29 - Connection Pooling Impact
**Learning:** Replacing one-off `requests.get` with `requests.Session` in a crawler loop yielded ~8.5% speedup even on localhost.
**Action:** Always use `requests.Session` for repetitive HTTP requests to the same domain.
