## 2024-05-22 - File-based Persistence Scalability
**Learning:** The application uses a local JSON file (`god_mode_history.json`) for persistence, and the `load_history_db` function reads and parses the entire file on every access (O(N) I/O). This is a specific architectural bottleneck that will degrade performance as usage history grows.
**Action:** For future performance tasks involving data persistence in this app, prioritize migrating from direct file I/O to an SQLite database or implementing in-memory caching with periodic writes.
