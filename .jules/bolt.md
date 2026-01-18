## 2026-01-18 - [Mocking Streamlit Side Effects]
**Learning:** When importing a Streamlit app into a test suite, top-level code (like st.columns) runs immediately. Mocking these with static return values fails if the app uses unpacking (e.g. `c1, c2 = st.columns(2)`).
**Action:** Use `side_effect` in mocks to return dynamic lists based on input arguments (e.g. `lambda n: [MagicMock()]*n`) to support varying column counts.
