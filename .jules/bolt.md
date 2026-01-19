## 2026-01-19 - Streamlit Testing & Side Effects
**Learning:** Streamlit applications often execute logic at the top level (e.g., inside `if st.button(...)`). Importing `app.py` for unit testing triggers this logic if mocks aren't carefully configured (e.g., `st.button.return_value = False`).
**Action:** When testing Streamlit apps, always mock the `streamlit` module *before* import and ensure interactive widgets return "falsey" values to prevent unwanted side-effects during test initialization.
