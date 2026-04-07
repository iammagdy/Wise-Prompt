## 2024-05-23 - Fast Membership Checks First
**Learning:** Checking string parsing functions like `urlparse(url).netloc` inside a tight loop with thousands of URLs causes significant slowdowns.
**Action:** Always perform O(1) set membership checks (`url in visited`) before doing expensive string manipulation.

## 2024-05-23 - O(1) Deque & Set For Queues
**Learning:** Using `queue.pop(0)` and `url in queue` with a standard Python list scales poorly under heavy crawler load, turning a simple BFS into an O(N^2) operation.
**Action:** Use `collections.deque` with an auxiliary `set` (`queued_urls`) for O(1) pops and O(1) membership checks.
