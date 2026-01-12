## 2024-05-22 - App Import Side Effects
**Learning:** `app.py` in Streamlit apps often executes code at the top level (e.g., `st.set_page_config`). To import it for testing, you must mock `streamlit` and other dependencies in `sys.modules` *before* import, and handle `st.columns`/`st.tabs` unpacking return values carefully.
**Action:** Always check for top-level side effects before importing app code in tests. Use a dedicated setup block to mock `sys.modules['streamlit']` with a MagicMock that supports `__getitem__` (for session state) and iterable return values (for unpacking).
