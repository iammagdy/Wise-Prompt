## 2026-01-23 - Streamlit Mocking Logic
**Learning:** Mocking `st.session_state` requires a custom class supporting both attribute and item access (`__getattr__`/`__setattr__` on `dict`), as `MagicMock` causes JSON serialization errors ("keys must be str") when used as keys or values in logic triggered during import.
**Action:** Always implement a `SessionState` mock class for Streamlit apps.

## 2026-01-23 - Crawling Optimization
**Learning:** `requests.Session()` provides connection pooling which is architecturally superior for crawlers, but localhost benchmarks over HTTP/1.1 may not show improvement due to minimal TCP overhead.
**Action:** Rely on architectural best practices for network I/O optimization when local benchmarks are inconclusive.
