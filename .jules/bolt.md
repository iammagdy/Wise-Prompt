## 2024-05-23 - Performance Baseline
**Learning:** The crawler uses `requests.get` inside a loop, creating a new TCP connection for every page. It also uses string concatenation `+=` to build the result.
**Action:** Replace `requests.get` with `requests.Session()` to reuse connections, and use a list with `''.join()` for efficient string building.
