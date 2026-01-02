## 2024-05-23 - [Streamlit Test Isolation]
**Learning:** Testing Streamlit apps (`app.py`) is tricky because importing the module triggers top-level code execution (like `st.set_page_config`).
**Action:** Always mock `streamlit` in `sys.modules` *before* importing the app module. Mock functions like `st.columns` must return iterables of the correct length to match unpacking statements.

## 2024-05-23 - [Crawler Optimization]
**Learning:** `requests.get` inside a loop creates a new TCP connection for every request, which is slow due to SSL handshakes.
**Action:** Use `requests.Session()` to reuse connections (keep-alive). This is a massive win for crawlers. Also, `deque` for queues and `list.join` for strings are standard python perf patterns.
