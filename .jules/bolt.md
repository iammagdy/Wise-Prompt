## 2024-05-23 - [Python String Concatenation & Request Session]
**Learning:** `requests.get` inside a loop creates a new connection for every request, which is inefficient for crawling the same domain. String concatenation (`+=`) in a loop is O(n^2).
**Action:** Use `requests.Session()` for connection pooling and list accumulation + `"".join()` for O(n) string building.
