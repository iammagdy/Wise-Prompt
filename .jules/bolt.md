## 2024-05-23 - [Streamlit Test Isolation]
**Learning:** Testing Streamlit apps requires heavy mocking of `sys.modules` BEFORE import because `st` commands execute at module level.
**Action:** Always create a `mock_st` with `sys.modules['streamlit'] = mock_st` before `import app` in tests.
