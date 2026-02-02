## 2026-02-02 - [app.py Import Side-Effects]
**Learning:** `app.py` executes Streamlit configuration code immediately upon import, causing errors in test environments unless `streamlit` is mocked beforehand.
**Action:** Always mock `sys.modules['streamlit']` and patch `st` methods (like `st.columns`, `st.tabs`) before importing `app.py` for testing.
