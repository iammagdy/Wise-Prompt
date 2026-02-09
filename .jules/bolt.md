## 2025-02-18 - Streamlit Mocking Pitfalls
**Learning:** Mocking Streamlit widgets like `st.button` returns truthy MagicMock objects by default, causing conditional logic (e.g., event handlers) to execute unexpectedly during import or testing.
**Action:** Explicitly set return values for interactive widgets (e.g., `st_mock.button.return_value = False`) when mocking Streamlit to prevent side effects.
