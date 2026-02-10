## 2025-02-17 - [Streamlit Import Complexity]
**Learning:** Importing `app.py` for testing is challenging because of top-level Streamlit calls (e.g., `st.set_page_config`, `st.tabs`). Mocking these requires correctly simulating return values (e.g., `st.tabs` returning a list of mocks) to avoid unpacking errors.
**Action:** Always mock `streamlit` and its components (`st.tabs`, `st.columns`, `st.sidebar`) before importing `app`, ensuring `side_effect` or `return_value` matches the expected unpacking structure.

## 2025-02-17 - [Queue Optimization in recursive_crawl]
**Learning:** `recursive_crawl` used a list for `queue` and linear scan for `visited` checks, leading to O(N) operations inside the loop. Switching to `deque` (O(1) pop) and a `queued_urls` set (O(1) lookup) improves scalability without sacrificing readability.
**Action:** Use `deque` for queues and `set` for membership checks by default in crawl logic.
