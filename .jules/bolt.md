## 2024-05-23 - Streamlit Component Mocking Complexity
**Learning:** Importing a Streamlit app file for testing executes the top-level code, which triggers `st.*` calls immediately.
**Action:** Always mock `streamlit` in `sys.modules` *before* importing the app module. Also, proactively mock controls like `st.button` and `st.chat_input` to return `False` or empty values to prevent event handler blocks from executing during import. Additionally, `st.tabs` and `st.columns` unpack values, so their mocks must return iterables of the correct length.
