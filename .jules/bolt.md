## 2024-05-23 - O(N) vs O(1) Queue Lookups
**Learning:** The `recursive_crawl` function used a list for the queue and performed `x in queue` checks ($O(N)$) for every link found on every page. This resulted in $O(N^2)$ complexity as the queue grew. Replacing it with a `deque` for $O(1)$ pops and a `seen_urls` set for $O(1)$ lookups reduced execution time from >400s (timeout) to ~5.8s for 1000 pages.
**Action:** Always use a `set` for membership checks when processing queues, instead of iterating through the list.
