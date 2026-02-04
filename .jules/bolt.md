## 2026-02-04 - String Concatenation and Queue Optimization
**Learning:** Python string concatenation (`+=`) in a loop creates a new string object each time, leading to O(N^2) complexity. Using `list.pop(0)` is O(N) but `deque.popleft()` is O(1).
**Action:** Replace `list +=` with `list.append()` and `"".join()`, and use `collections.deque` for FIFO queues in performance-critical loops like web crawling.
